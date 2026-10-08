#!/usr/bin/env python3
"""
train_pipeline.py — LeafLens Phase 5B Production Training Pipeline

Models:
  - Turmeric:  ConvNeXt-Tiny   (4 classes)
  - Citrus:    EfficientNetV2-S (18 classes)

Data:
  - All images loaded from Phase 4 split CSV manifests via ZIP-aware reader.
  - NEVER scans DATASET/ directly.

Features:
  - Multi-seed training (42, 123, 7) per crop.
  - Weighted Cross-Entropy Loss (weights from training set only).
  - AdamW optimizer + CosineAnnealingLR scheduler.
  - Best checkpoint saved by Validation Macro F1 (NOT accuracy).
  - Per-epoch CSV log + final experiment_summary.csv.
  - Smoke-test mode: verifies forward/backward pass, checks output dims.
  - Fully deterministic per seed (Python/NumPy/PyTorch/DataLoader).

Usage:
  python ml/scripts/train_pipeline.py --crop turmeric --smoke-test
  python ml/scripts/train_pipeline.py --crop turmeric --seed 42
  python ml/scripts/train_pipeline.py --crop citrus   --seed 42
  python ml/scripts/train_pipeline.py --run-all       # all crops × all seeds
"""

import argparse
import csv
import io
import json
import logging
import os
import random
import sys
import time
import zipfile
from collections import Counter
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("LeafLens.Train")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPLITS_DIR   = PROJECT_ROOT / "data" / "metadata" / "splits"
EXPS_DIR     = PROJECT_ROOT / "ml" / "experiments"

# ---------------------------------------------------------------------------
# Crop Configuration
# ---------------------------------------------------------------------------
CROP_CONFIG = {
    "turmeric": {
        "model":       "convnext_tiny",
        "num_classes": 4,
        "img_size":    224,
        "classes": ["Dry Leaf", "Healthy", "Leaf Blotch", "Leaf Spot"],
        "train_csv": SPLITS_DIR / "turmeric_train.csv",
        "val_csv":   SPLITS_DIR / "turmeric_val.csv",
        "test_csv":  SPLITS_DIR / "turmeric_test.csv",
        # Training hyperparameters
        "epochs":      50,
        "batch_size":  16,
        "lr":          1e-4,
        "weight_decay": 1e-2,
        "patience":    10,
        "num_workers": 0,   # set to 0 for ZIP-based loading (avoids pickle issues)
        "grad_cam_layer": "features.7",
    },
    "citrus": {
        "model":       "efficientnet_v2_s",
        "num_classes": 18,
        "img_size":    384,
        "classes": [
            "Algal_Leaf_Spot", "Anthracnose", "Bacterial Blight", "Black Spot",
            "Citrus Canker", "Citrus Hindu Mite", "Citrus Leafminer", "Citrus_Pest",
            "Citrus_Scab", "Curl Leaf", "Dry Leaf", "Greening", "Healthy",
            "Lemon_Sooty_Mold", "Melanose", "Spider Mites",
            "Swallowtail Larval Herbivory (Deficiency)", "Yellow_Spot",
        ],
        "train_csv": SPLITS_DIR / "citrus_train.csv",
        "val_csv":   SPLITS_DIR / "citrus_val.csv",
        "test_csv":  SPLITS_DIR / "citrus_test.csv",
        # Training hyperparameters
        "epochs":      40,
        "batch_size":  32,
        "lr":          1e-4,
        "weight_decay": 1e-2,
        "patience":    8,
        "num_workers": 0,
        "grad_cam_layer": "features.7",
    },
}

SEEDS = [42, 123, 7]

# ---------------------------------------------------------------------------
# ZIP-Aware Image Reader
def resolve_zip_path(raw_path: str) -> str:
    """
    Resolve zip file path.
    1. If raw_path exists directly on disk (local Windows environment), use it.
    2. Otherwise, check relative to PROJECT_ROOT / 'DATASET' / filename (Google Colab / Linux).
    3. Otherwise, check os.environ.get('DATASET_DIR') / filename.
    4. Otherwise, check current working directory DATASET / filename.
    """
    if os.path.exists(raw_path):
        return raw_path

    filename = Path(raw_path).name
    colab_path = PROJECT_ROOT / "DATASET" / filename
    if colab_path.exists():
        return str(colab_path)

    env_dataset = os.environ.get("DATASET_DIR")
    if env_dataset:
        env_path = Path(env_dataset) / filename
        if env_path.exists():
            return str(env_path)

    cwd_path = Path.cwd() / "DATASET" / filename
    if cwd_path.exists():
        return str(cwd_path)

    return raw_path


@lru_cache(maxsize=16)
def _open_zip(zip_path: str) -> zipfile.ZipFile:
    """Cache ZipFile handles (read-only) to avoid re-parsing central directories."""
    return zipfile.ZipFile(resolve_zip_path(zip_path), "r")


@lru_cache(maxsize=16)
def _open_inner_zip(outer_zip_path: str, inner_zip_name: str) -> zipfile.ZipFile:
    """Cache inner ZipFile handles in memory to avoid re-extracting and re-parsing inner ZIPs."""
    outer = _open_zip(outer_zip_path)
    inner_bytes = io.BytesIO(outer.read(inner_zip_name))
    return zipfile.ZipFile(inner_bytes, "r")


@lru_cache(maxsize=16)
def _open_nested_zip(outer_zip_path: str, mid_zip_name: str, inner_zip_name: str) -> zipfile.ZipFile:
    """Cache 3-level nested ZipFile handles."""
    mid = _open_inner_zip(outer_zip_path, mid_zip_name)
    inner_bytes = io.BytesIO(mid.read(inner_zip_name))
    return zipfile.ZipFile(inner_bytes, "r")


def open_pil_image(virtual_path: str) -> Image.Image:
    """
    Open PIL Image from a virtual ZIP path:
      single:   /a.zip#inner/path.jpg
      double:   /a.zip#b.zip#path.jpg
      triple:   /a.zip#b.zip#c.zip#path.jpg
    """
    segs = virtual_path.split(".zip#")
    n = len(segs)

    if n == 2:
        zf = _open_zip(segs[0] + ".zip")
        raw = zf.read(segs[1])
    elif n == 3:
        iz = _open_inner_zip(segs[0] + ".zip", segs[1] + ".zip")
        raw = iz.read(segs[2])
    elif n == 4:
        iz = _open_nested_zip(segs[0] + ".zip", segs[1] + ".zip", segs[2] + ".zip")
        raw = iz.read(segs[3])
    else:
        raise ValueError(f"Unsupported ZIP depth ({n-1}): {virtual_path}")

    return Image.open(io.BytesIO(raw)).convert("RGB")


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------
class LeafLensDataset(Dataset):
    """
    PyTorch Dataset that reads images from Phase 4 split CSV manifests.
    Images are stored in ZIP archives; paths use virtual '.zip#' notation.
    """

    def __init__(
        self,
        csv_path: Path,
        class_to_idx: Dict[str, int],
        transform=None,
    ):
        self.samples: List[Tuple[str, int]] = []
        self.transform = transform

        with open(csv_path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                label_str = row["final_class"].strip()
                if label_str not in class_to_idx:
                    raise KeyError(f"Unknown class '{label_str}' in {csv_path}")
                self.samples.append((row["absolute_path"].strip(), class_to_idx[label_str]))

        logger.debug(f"Loaded {len(self.samples)} samples from {csv_path.name}")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        path, label = self.samples[idx]
        img = open_pil_image(path)
        if self.transform:
            img = self.transform(img)
        return img, label


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]


def get_transforms(img_size: int, split: str):
    """
    Returns transforms for a given split.
    - train: conservative leaf-safe augmentation only on training set
    - val/test: deterministic resize + normalize, NO random ops
    """
    normalize = transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)

    if split == "train":
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            # Conservative photometric jitter: NO hue (preserves necrosis/chlorosis)
            transforms.ColorJitter(
                brightness=0.1, contrast=0.1, saturation=0.1, hue=0.0
            ),
            transforms.ToTensor(),
            normalize,
        ])
    else:
        # val, test — fully deterministic
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            normalize,
        ])


# ---------------------------------------------------------------------------
# Model Builder
# ---------------------------------------------------------------------------
def build_model(crop: str, num_classes: int) -> nn.Module:
    cfg = CROP_CONFIG[crop]
    arch = cfg["model"]

    if arch == "convnext_tiny":
        weights = models.ConvNeXt_Tiny_Weights.IMAGENET1K_V1
        model = models.convnext_tiny(weights=weights)
        # Replace classifier head: Sequential(LayerNorm2d, Flatten, Linear(768, 1000))
        in_features = model.classifier[2].in_features   # 768
        model.classifier[2] = nn.Linear(in_features, num_classes)
        logger.info(
            f"ConvNeXt-Tiny: head replaced → Linear({in_features}, {num_classes})"
        )

    elif arch == "efficientnet_v2_s":
        weights = models.EfficientNet_V2_S_Weights.IMAGENET1K_V1
        model = models.efficientnet_v2_s(weights=weights)
        # Replace classifier: Sequential(Dropout, Linear(1280, 1000))
        in_features = model.classifier[1].in_features   # 1280
        model.classifier[1] = nn.Linear(in_features, num_classes)
        logger.info(
            f"EfficientNetV2-S: head replaced → Linear({in_features}, {num_classes})"
        )

    else:
        raise ValueError(f"Unknown architecture: {arch}")

    return model


# ---------------------------------------------------------------------------
# Class Weights (computed from training set only)
# ---------------------------------------------------------------------------
def compute_class_weights(
    train_csv: Path, class_to_idx: Dict[str, int], device: torch.device
) -> torch.Tensor:
    """
    Compute inverse-frequency class weights from the TRAINING SET only.
    Weight_c = total_samples / (num_classes * count_c)
    This is scikit-learn's 'balanced' strategy.
    """
    with open(train_csv, encoding="utf-8", newline="") as f:
        counts = Counter(row["final_class"].strip() for row in csv.DictReader(f))

    num_classes = len(class_to_idx)
    total = sum(counts.values())
    weights = torch.zeros(num_classes)
    for cls, idx in class_to_idx.items():
        weights[idx] = total / (num_classes * counts[cls])

    logger.info("Class weights (balanced inverse-frequency from train set):")
    for cls, idx in sorted(class_to_idx.items(), key=lambda x: x[1]):
        logger.info(f"  [{idx}] {cls}: count={counts[cls]}, weight={weights[idx]:.4f}")

    return weights.to(device)


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------
def set_seed(seed: int):
    """Set all RNG seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark     = False
    os.environ["PYTHONHASHSEED"] = str(seed)


def seed_worker(worker_id: int):
    """DataLoader worker seed function."""
    worker_seed = torch.initial_seed() % (2**32)
    np.random.seed(worker_seed)
    random.seed(worker_seed)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def compute_metrics(
    all_labels: List[int],
    all_preds:  List[int],
    num_classes: int,
) -> Dict:
    """Compute accuracy, macro P/R/F1, and per-class F1."""
    labels_arr = np.array(all_labels)
    preds_arr  = np.array(all_preds)

    acc = accuracy_score(labels_arr, preds_arr)
    mac_p  = precision_score(labels_arr, preds_arr, average="macro", zero_division=0)
    mac_r  = recall_score   (labels_arr, preds_arr, average="macro", zero_division=0)
    mac_f1 = f1_score       (labels_arr, preds_arr, average="macro", zero_division=0)
    per_f1 = f1_score       (labels_arr, preds_arr, average=None,    zero_division=0,
                              labels=list(range(num_classes)))
    cm     = confusion_matrix(labels_arr, preds_arr, labels=list(range(num_classes)))

    return {
        "accuracy":        float(acc),
        "macro_precision": float(mac_p),
        "macro_recall":    float(mac_r),
        "macro_f1":        float(mac_f1),
        "per_class_f1":    [float(x) for x in per_f1],
        "confusion_matrix": cm.tolist(),
    }


# ---------------------------------------------------------------------------
# One Epoch
# ---------------------------------------------------------------------------
def run_epoch(
    model:     nn.Module,
    loader:    DataLoader,
    criterion: nn.Module,
    optimizer: Optional[torch.optim.Optimizer],
    device:    torch.device,
    num_classes: int,
    is_train:  bool,
) -> Tuple[float, Dict]:
    """Run one train or eval epoch. Returns (avg_loss, metrics_dict)."""
    model.train(is_train)
    total_loss = 0.0
    all_labels, all_preds = [], []
    n_batches = 0

    ctx = torch.enable_grad() if is_train else torch.no_grad()
    with ctx:
        for images, labels in loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            logits = model(images)
            loss   = criterion(logits, labels)

            if is_train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            total_loss  += loss.item()
            preds        = logits.argmax(dim=1)
            all_labels  += labels.cpu().tolist()
            all_preds   += preds.cpu().tolist()
            n_batches   += 1

    avg_loss = total_loss / max(n_batches, 1)
    metrics  = compute_metrics(all_labels, all_preds, num_classes)
    return avg_loss, metrics


# ---------------------------------------------------------------------------
# Smoke Test
# ---------------------------------------------------------------------------
def smoke_test(crop: str, device: torch.device) -> bool:
    """
    Verify forward + backward pass with a small real batch.
    Returns True if all checks pass.
    """
    logger.info(f"{'='*60}")
    logger.info(f"SMOKE TEST — {crop.upper()}")
    logger.info(f"{'='*60}")

    cfg        = CROP_CONFIG[crop]
    num_classes = cfg["num_classes"]
    img_size   = cfg["img_size"]
    batch_size = 2

    set_seed(42)

    # Build model
    model = build_model(crop, num_classes).to(device)

    # Build a tiny dataloader (first 4 samples from train CSV)
    class_to_idx = {cls: i for i, cls in enumerate(cfg["classes"])}
    train_tf = get_transforms(img_size, "train")

    with open(cfg["train_csv"], encoding="utf-8", newline="") as f:
        first_rows = list(csv.DictReader(f))[:4]

    samples = []
    for row in first_rows:
        p   = row["absolute_path"].strip()
        cls = row["final_class"].strip()
        img = open_pil_image(p)
        tensor = train_tf(img)
        samples.append((tensor, class_to_idx[cls]))

    images = torch.stack([s[0] for s in samples]).to(device)
    labels = torch.tensor([s[1] for s in samples], dtype=torch.long).to(device)

    # Forward pass
    model.train()
    logits = model(images)
    expected_shape = (len(samples), num_classes)
    assert logits.shape == torch.Size(expected_shape), (
        f"Output shape mismatch: got {tuple(logits.shape)}, expected {expected_shape}"
    )
    logger.info(f"  [OK] Forward pass output shape: {tuple(logits.shape)}")

    # Loss
    criterion = nn.CrossEntropyLoss()
    loss = criterion(logits, labels)
    assert torch.isfinite(loss), f"Loss is not finite: {loss.item()}"
    logger.info(f"  [OK] Loss: {loss.item():.4f} (finite)")

    # Backward pass
    loss.backward()
    logger.info(f"  [OK] Backward pass completed")

    # Gradient check on classifier head
    if crop == "turmeric":
        head_param = model.classifier[2].weight
    else:
        head_param = model.classifier[1].weight
    assert head_param.grad is not None, "Classifier head gradient is None"
    assert head_param.grad.abs().sum().item() > 0, "Classifier head gradient is zero"
    logger.info(f"  [OK] Classifier head gradient norm: {head_param.grad.norm().item():.6f}")

    # Optimizer step
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-2)
    optimizer.step()
    optimizer.zero_grad()
    logger.info(f"  [OK] Optimizer step completed")

    logger.info(f"  SMOKE TEST PASSED for {crop.upper()}")
    return True


# ---------------------------------------------------------------------------
# Training Loop
# ---------------------------------------------------------------------------
def train_one_seed(
    crop:   str,
    seed:   int,
    device: torch.device,
) -> Dict:
    """
    Train one crop × seed combination.
    Returns a results dict with best metrics.
    """
    cfg         = CROP_CONFIG[crop]
    num_classes = cfg["num_classes"]
    img_size    = cfg["img_size"]
    class_to_idx = {cls: i for i, cls in enumerate(cfg["classes"])}
    idx_to_class = {i: cls for cls, i in class_to_idx.items()}

    # Experiment output directory
    arch_name = cfg["model"]
    exp_dir   = EXPS_DIR / crop / arch_name / f"seed_{seed}"
    exp_dir.mkdir(parents=True, exist_ok=True)

    # Prevent overwriting completed runs
    summary_file = exp_dir / "experiment_summary.json"
    if summary_file.exists():
        logger.warning(
            f"Experiment already exists at {exp_dir}. Skipping to avoid overwrite."
        )
        with open(summary_file, encoding="utf-8") as f:
            return json.load(f)

    logger.info(f"{'='*60}")
    logger.info(f"TRAINING — {crop.upper()} | {arch_name} | seed={seed}")
    logger.info(f"Output dir: {exp_dir}")
    logger.info(f"{'='*60}")

    set_seed(seed)

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    train_tf = get_transforms(img_size, "train")
    eval_tf  = get_transforms(img_size, "val")

    g = torch.Generator()
    g.manual_seed(seed)

    train_ds = LeafLensDataset(cfg["train_csv"], class_to_idx, train_tf)
    val_ds   = LeafLensDataset(cfg["val_csv"],   class_to_idx, eval_tf)

    train_loader = DataLoader(
        train_ds,
        batch_size=cfg["batch_size"],
        shuffle=True,
        num_workers=cfg["num_workers"],
        worker_init_fn=seed_worker,
        generator=g,
        pin_memory=(device.type == "cuda"),
        persistent_workers=False,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=cfg["batch_size"],
        shuffle=False,
        num_workers=cfg["num_workers"],
        pin_memory=(device.type == "cuda"),
        persistent_workers=False,
    )

    logger.info(
        f"Train: {len(train_ds)} imgs | Val: {len(val_ds)} imgs | "
        f"img_size={img_size} | batch={cfg['batch_size']}"
    )

    # ------------------------------------------------------------------
    # Model
    # ------------------------------------------------------------------
    model = build_model(crop, num_classes).to(device)

    # ------------------------------------------------------------------
    # Loss (class-weighted, TRAINING SET ONLY)
    # ------------------------------------------------------------------
    class_weights = compute_class_weights(cfg["train_csv"], class_to_idx, device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # ------------------------------------------------------------------
    # Optimizer + Scheduler
    # ------------------------------------------------------------------
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg["lr"],
        weight_decay=cfg["weight_decay"],
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=cfg["epochs"], eta_min=1e-6
    )

    # ------------------------------------------------------------------
    # Training history log
    # ------------------------------------------------------------------
    history_path = exp_dir / "training_history.csv"
    history_fieldnames = [
        "epoch", "train_loss", "val_loss", "val_accuracy",
        "val_macro_precision", "val_macro_recall", "val_macro_f1",
        "learning_rate",
    ]
    with open(history_path, "w", newline="", encoding="utf-8") as hf:
        writer = csv.DictWriter(hf, fieldnames=history_fieldnames)
        writer.writeheader()

    # ------------------------------------------------------------------
    # Training Loop
    # ------------------------------------------------------------------
    best_val_f1     = -1.0
    best_epoch      = -1
    best_ckpt_path  = exp_dir / "best_model.pt"
    patience_counter = 0
    history         = []

    t0 = time.time()

    for epoch in range(1, cfg["epochs"] + 1):
        current_lr = optimizer.param_groups[0]["lr"]

        # Train
        train_loss, _ = run_epoch(
            model, train_loader, criterion, optimizer, device, num_classes, is_train=True
        )
        scheduler.step()

        # Validate
        val_loss, val_metrics = run_epoch(
            model, val_loader, criterion, None, device, num_classes, is_train=False
        )

        val_f1  = val_metrics["macro_f1"]
        val_acc = val_metrics["accuracy"]

        elapsed = time.time() - t0
        logger.info(
            f"Epoch {epoch:3d}/{cfg['epochs']} | "
            f"train_loss={train_loss:.4f} | val_loss={val_loss:.4f} | "
            f"val_acc={val_acc:.4f} | val_macro_f1={val_f1:.4f} | "
            f"lr={current_lr:.2e} | elapsed={elapsed:.0f}s"
        )

        # Per-class F1 at every 5th epoch
        if epoch % 5 == 0 or epoch == 1:
            for i, f1_val in enumerate(val_metrics["per_class_f1"]):
                logger.info(f"  [{i}] {idx_to_class[i]}: F1={f1_val:.4f}")

        # Log to CSV
        row = {
            "epoch":                epoch,
            "train_loss":           round(train_loss, 6),
            "val_loss":             round(val_loss, 6),
            "val_accuracy":         round(val_acc, 6),
            "val_macro_precision":  round(val_metrics["macro_precision"], 6),
            "val_macro_recall":     round(val_metrics["macro_recall"], 6),
            "val_macro_f1":         round(val_f1, 6),
            "learning_rate":        current_lr,
        }
        with open(history_path, "a", newline="", encoding="utf-8") as hf:
            csv.DictWriter(hf, fieldnames=history_fieldnames).writerow(row)
        history.append(row)

        # Best checkpoint (by val Macro F1)
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_epoch  = epoch
            patience_counter = 0

            best_ckpt_path = exp_dir / "best_model.pt"
            torch.save(
                {
                    "epoch":           epoch,
                    "model_state_dict": model.state_dict(),
                    "val_macro_f1":    val_f1,
                    "val_accuracy":    val_acc,
                    "class_to_idx":    class_to_idx,
                    "crop":            crop,
                    "model":           cfg["model"],
                    "seed":            seed,
                    "img_size":        img_size,
                },
                best_ckpt_path,
            )
        else:
            patience_counter += 1

        # Print progress line after EVERY epoch in required format
        model_display = "ConvNeXt-Tiny" if "convnext" in cfg["model"] else "EfficientNetV2-S"
        mins, secs = divmod(int(elapsed), 60)
        elapsed_str = f"{mins}m {secs:02d}s" if mins > 0 else f"{secs}s"
        print(
            f"\n[{crop.capitalize()} | {model_display} | Seed {seed}]\n"
            f"Epoch {epoch}/{cfg['epochs']}\n"
            f"Train Loss: {train_loss:.4f}\n"
            f"Val Loss: {val_loss:.4f}\n"
            f"Val Accuracy: {val_acc:.4f}\n"
            f"Val Macro F1: {val_f1:.4f}\n"
            f"Best Macro F1: {best_val_f1:.4f}\n"
            f"Elapsed: {elapsed_str}\n",
            flush=True,
        )

        if patience_counter >= cfg["patience"]:
            logger.info(
                f"Early stopping at epoch {epoch} "
                f"(no improvement for {cfg['patience']} epochs)"
            )
            break

    # ------------------------------------------------------------------
    # Final checkpoint
    # ------------------------------------------------------------------
    final_ckpt_path = exp_dir / "final_model.pt"
    torch.save(
        {
            "epoch":           epoch,
            "model_state_dict": model.state_dict(),
            "class_to_idx":    class_to_idx,
            "crop":            crop,
            "model":           cfg["model"],
            "seed":            seed,
            "img_size":        img_size,
        },
        final_ckpt_path,
    )

    # ------------------------------------------------------------------
    # Per-class F1 from best checkpoint run: reload best model for final val metrics
    # ------------------------------------------------------------------
    logger.info(f"Reloading best checkpoint (epoch {best_epoch}) for final metrics...")
    ckpt = torch.load(best_ckpt_path, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])

    _, best_val_metrics = run_epoch(
        model, val_loader, criterion, None, device, num_classes, is_train=False
    )

    # ------------------------------------------------------------------
    # Experiment summary
    # ------------------------------------------------------------------
    per_class_f1_named = {
        idx_to_class[i]: round(f1_val, 6)
        for i, f1_val in enumerate(best_val_metrics["per_class_f1"])
    }

    summary = {
        "crop":                  crop,
        "model":                 cfg["model"],
        "seed":                  seed,
        "num_classes":           num_classes,
        "classes":               cfg["classes"],
        "img_size":              img_size,
        "epochs_trained":        epoch,
        "best_epoch":            best_epoch,
        "best_val_macro_f1":     round(best_val_f1, 6),
        "best_val_accuracy":     round(best_val_metrics["accuracy"], 6),
        "best_val_macro_precision": round(best_val_metrics["macro_precision"], 6),
        "best_val_macro_recall": round(best_val_metrics["macro_recall"], 6),
        "per_class_f1":          per_class_f1_named,
        "confusion_matrix":      best_val_metrics["confusion_matrix"],
        "hyperparameters": {
            "optimizer":     "AdamW",
            "lr":            cfg["lr"],
            "weight_decay":  cfg["weight_decay"],
            "scheduler":     "CosineAnnealingLR",
            "batch_size":    cfg["batch_size"],
            "loss":          "CrossEntropyLoss (class-weighted, inverse-frequency)",
            "patience":      cfg["patience"],
        },
        "augmentation": {
            "train": ["RandomHorizontalFlip(p=0.5)", "RandomVerticalFlip(p=0.5)",
                      "RandomRotation(15)", "ColorJitter(b=0.1,c=0.1,s=0.1,hue=0.0)",
                      "ToTensor", "Normalize(ImageNet)"],
            "val_test": ["Resize", "ToTensor", "Normalize(ImageNet)"],
        },
        "best_checkpoint":  str(best_ckpt_path),
        "final_checkpoint": str(final_ckpt_path),
        "training_history": str(history_path),
        "train_images":     len(train_ds),
        "val_images":       len(val_ds),
        "completed_at":     datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Experiment summary saved → {summary_file}")
    logger.info(
        f"DONE: {crop.upper()} seed={seed} | "
        f"best_epoch={best_epoch} | best_val_macro_f1={best_val_f1:.4f}"
    )

    model_display = "ConvNeXt-Tiny" if "convnext" in cfg["model"] else "EfficientNetV2-S"
    print(
        f"\nEXPERIMENT 1 COMPLETE\n"
        f"Best Epoch: {best_epoch}\n"
        f"Best Val Macro F1: {best_val_f1:.4f}\n"
        f"Best Val Accuracy: {best_val_metrics['accuracy']:.4f}\n"
        f"Checkpoint: {best_ckpt_path}\n"
        f"Next experiment: Turmeric ConvNeXt-Tiny Seed 123\n",
        flush=True,
    )
    return summary


# ---------------------------------------------------------------------------
# Multi-Seed Aggregator
# ---------------------------------------------------------------------------
def aggregate_seeds(crop: str, seed_results: List[Dict]) -> Dict:
    """Compute mean ± std across seeds for primary metrics."""
    f1s  = [r["best_val_macro_f1"] for r in seed_results]
    accs = [r["best_val_accuracy"]  for r in seed_results]

    return {
        "crop":                     crop,
        "model":                    seed_results[0]["model"],
        "seeds":                    [r["seed"] for r in seed_results],
        "per_seed_val_macro_f1":    f1s,
        "mean_val_macro_f1":        float(np.mean(f1s)),
        "std_val_macro_f1":         float(np.std(f1s, ddof=1) if len(f1s) > 1 else 0.0),
        "per_seed_val_accuracy":    accs,
        "mean_val_accuracy":        float(np.mean(accs)),
        "std_val_accuracy":         float(np.std(accs, ddof=1) if len(accs) > 1 else 0.0),
        "best_seed":                seed_results[int(np.argmax(f1s))]["seed"],
        "best_val_macro_f1":        float(max(f1s)),
    }


# ---------------------------------------------------------------------------
# Experiment Summary CSV
# ---------------------------------------------------------------------------
def write_experiment_summary_csv(all_results: List[Dict]):
    """Write a flat CSV with one row per crop×seed experiment."""
    out_path = EXPS_DIR / "experiment_summary.csv"
    fieldnames = [
        "crop", "model", "seed", "best_epoch", "epochs_trained",
        "best_val_macro_f1", "best_val_accuracy",
        "best_val_macro_precision", "best_val_macro_recall",
        "train_images", "val_images", "img_size", "batch_size",
        "lr", "weight_decay", "completed_at", "best_checkpoint",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in all_results:
            row = {k: r.get(k, r.get("hyperparameters", {}).get(k, "")) for k in fieldnames}
            # Flatten hyperparameters
            row["batch_size"]    = r.get("hyperparameters", {}).get("batch_size", "")
            row["lr"]            = r.get("hyperparameters", {}).get("lr", "")
            row["weight_decay"]  = r.get("hyperparameters", {}).get("weight_decay", "")
            writer.writerow(row)
    logger.info(f"Experiment summary CSV → {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="LeafLens Phase 5B Training Pipeline"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--run-all",    action="store_true",
                       help="Train all crops × all seeds sequentially")
    group.add_argument("--smoke-test", action="store_true",
                       help="Run smoke tests only (no full training)")
    parser.add_argument("--crop",  choices=["turmeric", "citrus"],
                        help="Crop to train (use with --seed)")
    parser.add_argument("--seed",  type=int, choices=[42, 123, 7],
                        help="Seed to use (use with --crop)")
    args = parser.parse_args()

    device = torch.device(
        "cuda" if torch.cuda.is_available() else
        "mps"  if torch.backends.mps.is_available() else
        "cpu"
    )
    logger.info(f"Compute device: {device}")

    # ── Smoke tests ──────────────────────────────────────────────────
    if args.smoke_test:
        logger.info("Running smoke tests for all models...")
        for crop in ["turmeric", "citrus"]:
            ok = smoke_test(crop, device)
            if not ok:
                logger.error(f"Smoke test FAILED for {crop}. Aborting.")
                sys.exit(1)
        logger.info("All smoke tests PASSED. Safe to run full training.")
        return

    # ── Single crop × seed ───────────────────────────────────────────
    if args.crop and args.seed is not None:
        results = train_one_seed(args.crop, args.seed, device)
        write_experiment_summary_csv([results])
        return

    # ── Run all ──────────────────────────────────────────────────────
    if args.run_all:
        all_results = []
        agg_all     = []

        for crop in ["turmeric", "citrus"]:
            # Smoke test first
            logger.info(f"Smoke-testing {crop}...")
            ok = smoke_test(crop, device)
            if not ok:
                logger.error(f"Smoke test FAILED for {crop}. Aborting all training.")
                sys.exit(1)
            logger.info(f"Smoke test PASSED for {crop}.")

            seed_results = []
            for seed in SEEDS:
                result = train_one_seed(crop, seed, device)
                seed_results.append(result)
                all_results.append(result)

            agg = aggregate_seeds(crop, seed_results)
            agg_all.append(agg)
            logger.info(
                f"{'='*60}\n"
                f"{crop.upper()} AGGREGATE ACROSS SEEDS {SEEDS}:\n"
                f"  Macro F1:  {agg['mean_val_macro_f1']:.4f} ± {agg['std_val_macro_f1']:.4f}\n"
                f"  Accuracy:  {agg['mean_val_accuracy']:.4f} ± {agg['std_val_accuracy']:.4f}\n"
                f"  Best seed: {agg['best_seed']} (F1={agg['best_val_macro_f1']:.4f})\n"
                f"{'='*60}"
            )

            # Save aggregate per crop
            agg_path = EXPS_DIR / crop / CROP_CONFIG[crop]["model"] / "seed_aggregate.json"
            with open(agg_path, "w", encoding="utf-8") as f:
                json.dump(agg, f, indent=2)

        summary_csv = write_experiment_summary_csv(all_results)

        # Final report
        logger.info("\n" + "="*60)
        logger.info("PHASE 5B TRAINING COMPLETE")
        logger.info("="*60)
        for agg in agg_all:
            logger.info(
                f"{agg['crop'].upper()} ({agg['model']}): "
                f"Macro F1 = {agg['mean_val_macro_f1']:.4f} ± {agg['std_val_macro_f1']:.4f}"
            )
        logger.info(f"Summary CSV: {summary_csv}")
        logger.info("="*60)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
