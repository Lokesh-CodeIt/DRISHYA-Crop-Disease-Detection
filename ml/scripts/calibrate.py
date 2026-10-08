#!/usr/bin/env python3
"""
calibrate.py - DRISHYA ML Upgrade Step A: Trustworthy Confidence Calibration Pipeline

Purpose:
    Applies post-hoc Temperature Scaling (Guo et al., 2017) to active Turmeric (ConvNeXt-Tiny)
    and Citrus (EfficientNetV2-S) classifiers.
    Finds optimal scalar temperature T > 0 on validation split logits by minimizing Negative Log Likelihood (NLL).
    Evaluates Expected Calibration Error (ECE), Multiclass Brier Score, NLL, Accuracy, Macro F1,
    mean confidence, and rejection rate (at threshold 0.65) on validation and clean test splits.

Crucial Constraints:
    - Validation split is used EXCLUSIVELY for fitting T.
    - Test split is evaluated strictly post-fit and never used for optimization.
    - Never uses TESTING/ folder.
    - Classifiers are NOT retrained; model weights remain unaltered.
    - Top-1 predictions, accuracy, and Macro F1 remain invariant under temperature scaling.
"""

import os
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import json
import time
import logging
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
import torch
import torch.nn as nn
import torch.optim as optim

from ml.scripts.zip_image_reader import open_pil_image
from backend.app.ml.registry import get_active_model_config, ModelConfig
from backend.app.ml.model_builder import load_trained_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DRISHYA.Calibrate")

CALIBRATION_DIR = PROJECT_ROOT / "ml" / "calibration"
CACHE_DIR = CALIBRATION_DIR / "cache"


# ===========================================================================
# 1. Dataset & Logit Extraction
# ===========================================================================
def extract_split_logits(
    crop: str,
    split: str,
    model: nn.Module,
    config: ModelConfig,
    csv_path: Path,
    batch_size: int = 32,
    force_extract: bool = False,
) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
    """
    Extracts raw logits and ground-truth integer labels for a crop split.
    Caches results to ml/calibration/cache/{crop}_{split}_logits.npz to allow
    instant re-runs without repeating heavy CPU forward passes.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{crop}_{split}_logits.npz"

    if cache_file.exists() and not force_extract:
        logger.info(f"Loading cached logits from {cache_file}")
        data = np.load(cache_file, allow_pickle=True)
        return data["logits"], data["labels"], list(data["image_ids"]), list(data["classes"])

    logger.info(f"Extracting logits for crop='{crop}', split='{split}' from {csv_path}...")
    if not csv_path.exists():
        raise FileNotFoundError(f"Split CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    total_samples = len(df)
    logger.info(f"Total samples to process: {total_samples}")

    class_to_idx = config.get_class_to_idx()
    ordered_classes = config.get_classes()
    img_size = config.img_size

    # Mean and standard deviation for ImageNet normalization
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)

    model.eval()
    all_logits = []
    all_labels = []
    all_image_ids = []

    start_time = time.time()
    num_batches = int(np.ceil(total_samples / batch_size))

    for b_idx in range(num_batches):
        batch_df = df.iloc[b_idx * batch_size : (b_idx + 1) * batch_size]
        tensors = []
        labels = []
        image_ids = []

        for _, row in batch_df.iterrows():
            img_path = row["absolute_path"]
            cls_name = row["final_class"]
            if cls_name not in class_to_idx:
                raise ValueError(f"Class '{cls_name}' not in config class mapping: {list(class_to_idx.keys())}")

            cls_idx = class_to_idx[cls_name]
            labels.append(cls_idx)
            image_ids.append(row["image_id"])

            # Read image via zip_image_reader
            img = open_pil_image(img_path).resize((img_size, img_size))
            img_arr = np.array(img, dtype=np.float32) / 255.0
            if img_arr.ndim == 2:  # Grayscale fallback
                img_arr = np.stack([img_arr] * 3, axis=-1)
            elif img_arr.shape[2] == 4:  # RGBA fallback
                img_arr = img_arr[:, :, :3]

            tensor = torch.from_numpy(img_arr).permute(2, 0, 1)
            normalized = (tensor - mean) / std
            tensors.append(normalized)

        batch_tensor = torch.stack(tensors)
        with torch.inference_mode():
            batch_logits = model(batch_tensor)

        all_logits.append(batch_logits.cpu().numpy())
        all_labels.extend(labels)
        all_image_ids.extend(image_ids)

        processed = min((b_idx + 1) * batch_size, total_samples)
        elapsed = time.time() - start_time
        samples_per_sec = processed / elapsed if elapsed > 0 else 0
        if (b_idx + 1) % 5 == 0 or processed == total_samples:
            logger.info(
                f"  [{crop} {split}] Batch {b_idx + 1}/{num_batches} | "
                f"Samples: {processed}/{total_samples} ({processed/total_samples*100:.1f}%) | "
                f"Speed: {samples_per_sec:.1f} samples/s | Elapsed: {elapsed:.1f}s"
            )

    logits_arr = np.concatenate(all_logits, axis=0).astype(np.float32)
    labels_arr = np.array(all_labels, dtype=np.int64)

    # Save to cache
    np.savez_compressed(
        cache_file,
        logits=logits_arr,
        labels=labels_arr,
        image_ids=np.array(all_image_ids),
        classes=np.array(ordered_classes),
    )
    logger.info(f"✓ Cached {len(logits_arr)} logits to {cache_file}")

    return logits_arr, labels_arr, all_image_ids, ordered_classes


# ===========================================================================
# 2. Metric Computation Functions
# ===========================================================================
def softmax(x: np.ndarray) -> np.ndarray:
    """Numerically stable softmax."""
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / np.sum(e_x, axis=-1, keepdims=True)


def compute_ece_and_bins(
    probs: np.ndarray,
    labels: np.ndarray,
    n_bins: int = 15,
) -> Tuple[float, float, List[Dict[str, Any]]]:
    """
    Computes 15-bin equal-width Expected Calibration Error (ECE),
    Maximum Calibration Error (MCE), and per-bin reliability diagram metadata.
    """
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == labels).astype(np.float32)
    n_samples = len(labels)

    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    mce = 0.0
    bin_details = []

    for i in range(n_bins):
        lower = float(bin_boundaries[i])
        upper = float(bin_boundaries[i + 1])

        if i == n_bins - 1:
            in_bin = (confidences >= lower) & (confidences <= upper)
        else:
            in_bin = (confidences >= lower) & (confidences < upper)

        count = int(np.sum(in_bin))
        prop = count / n_samples if n_samples > 0 else 0.0

        if count > 0:
            bin_acc = float(np.mean(accuracies[in_bin]))
            bin_conf = float(np.mean(confidences[in_bin]))
            gap = float(np.abs(bin_acc - bin_conf))
            ece += gap * prop
            mce = max(mce, gap)
        else:
            bin_acc = None
            bin_conf = None
            gap = 0.0

        bin_details.append({
            "bin_index": i,
            "bin_lower": round(lower, 4),
            "bin_upper": round(upper, 4),
            "sample_count": count,
            "bin_accuracy": round(bin_acc, 6) if bin_acc is not None else None,
            "bin_confidence": round(bin_conf, 6) if bin_conf is not None else None,
            "calibration_gap": round(gap, 6),
        })

    return float(ece), float(mce), bin_details


def compute_brier_score(probs: np.ndarray, labels: np.ndarray, num_classes: int) -> float:
    """
    Computes standard multiclass Brier score:
    (1 / N) * sum_i sum_k (p_ik - y_ik)^2
    where y_ik is the one-hot indicator of class k.
    """
    one_hot = np.zeros_like(probs)
    one_hot[np.arange(len(labels)), labels] = 1.0
    brier = np.mean(np.sum((probs - one_hot) ** 2, axis=1))
    return float(brier)


def compute_nll(logits: np.ndarray, labels: np.ndarray, temperature: float = 1.0) -> float:
    """
    Computes Negative Log Likelihood (Cross-Entropy Loss) on logits / temperature.
    """
    t_val = max(float(temperature), 1e-4)
    scaled_logits = logits / t_val
    t_logits = torch.from_numpy(scaled_logits).float()
    t_labels = torch.from_numpy(labels).long()
    loss_fn = nn.CrossEntropyLoss()
    with torch.no_grad():
        loss = loss_fn(t_logits, t_labels).item()
    return float(loss)


def evaluate_metrics(
    logits: np.ndarray,
    labels: np.ndarray,
    temperature: float = 1.0,
    rejection_threshold: float = 0.65,
    n_bins: int = 15,
) -> Dict[str, Any]:
    """
    Computes full suite of classification and calibration metrics:
    ECE, MCE, NLL, Brier score, Accuracy, Macro F1, Mean Confidence,
    Rejection Rate (at 0.65), and Reliability Bin details.
    """
    t_val = max(float(temperature), 1e-4)
    scaled_logits = logits / t_val
    probs = softmax(scaled_logits)

    predictions = np.argmax(probs, axis=1)
    confidences = np.max(probs, axis=1)
    num_classes = logits.shape[1]
    n_samples = len(labels)

    acc = float(np.mean(predictions == labels))
    macro_f1 = float(f1_score(labels, predictions, average="macro", zero_division=0))
    nll = compute_nll(logits, labels, temperature=t_val)
    brier = compute_brier_score(probs, labels, num_classes)
    ece, mce, bin_details = compute_ece_and_bins(probs, labels, n_bins=n_bins)
    mean_conf = float(np.mean(confidences))

    is_rejected = confidences < rejection_threshold
    rejection_count = int(np.sum(is_rejected))
    rejection_rate = float(rejection_count / n_samples) if n_samples > 0 else 0.0

    return {
        "temperature": float(t_val),
        "num_samples": n_samples,
        "num_classes": num_classes,
        "accuracy": round(acc, 6),
        "macro_f1": round(macro_f1, 6),
        "nll": round(nll, 6),
        "brier_score": round(brier, 6),
        "ece": round(ece, 6),
        "mce": round(mce, 6),
        "mean_confidence": round(mean_conf, 6),
        "rejection_threshold": rejection_threshold,
        "rejection_count": rejection_count,
        "rejection_rate": round(rejection_rate, 6),
        "bins": bin_details,
    }


# ===========================================================================
# 3. Temperature Optimization (Validation Split Only)
# ===========================================================================
def fit_temperature(val_logits: np.ndarray, val_labels: np.ndarray) -> float:
    """
    Optimizes scalar temperature T > 0 by minimizing Negative Log Likelihood
    on validation logits only using L-BFGS.
    Parameterizes T = exp(s) where s is unconstrained real parameter.
    """
    t_logits = torch.from_numpy(val_logits).float()
    t_labels = torch.from_numpy(val_labels).long()

    # Parameterize log-temperature: s = log(T), initialized to 0 (T = 1.0)
    log_temp = nn.Parameter(torch.zeros(1, dtype=torch.float32))
    nll_criterion = nn.CrossEntropyLoss()

    optimizer = optim.LBFGS(
        [log_temp],
        lr=0.05,
        max_iter=100,
        line_search_fn="strong_wolfe",
        tolerance_grad=1e-7,
        tolerance_change=1e-9,
    )

    def eval_loss():
        optimizer.zero_grad()
        T = torch.exp(log_temp)
        loss = nll_criterion(t_logits / T, t_labels)
        loss.backward()
        return loss

    optimizer.step(eval_loss)

    optimal_t = float(torch.exp(log_temp).item())
    logger.info(f"L-BFGS optimization complete: Optimal T = {optimal_t:.6f}")
    return optimal_t


# ===========================================================================
# 4. Calibration Pipeline Orchestrator
# ===========================================================================
def calibrate_crop(
    crop: str,
    batch_size: int = 32,
    force_extract: bool = False,
    rejection_threshold: float = 0.65,
) -> Dict[str, Any]:
    """
    Runs full calibration pipeline for a single crop:
    1. Loads active model & config
    2. Extracts or loads validation and test logits
    3. Computes pre-calibration metrics on validation and test splits
    4. Fits optimal temperature T ON VALIDATION SPLIT ONLY
    5. Computes post-calibration metrics on validation and test splits
    6. Verifies prediction invariance (accuracy and macro F1 unchanged)
    7. Exports calibration JSON artifacts
    """
    logger.info(f"\n{'='*70}\nCALIBRATING CROP: {crop.upper()}\n{'='*70}")

    config = get_active_model_config(crop)
    model, meta = load_trained_model(config, map_location="cpu")
    model.eval()

    val_csv = PROJECT_ROOT / "data" / "metadata" / "splits" / f"{crop}_val.csv"
    test_csv = PROJECT_ROOT / "data" / "metadata" / "splits" / f"{crop}_test.csv"

    # Step 1: Extract logits
    val_logits, val_labels, val_ids, classes = extract_split_logits(
        crop=crop,
        split="val",
        model=model,
        config=config,
        csv_path=val_csv,
        batch_size=batch_size,
        force_extract=force_extract,
    )

    test_logits, test_labels, test_ids, _ = extract_split_logits(
        crop=crop,
        split="test",
        model=model,
        config=config,
        csv_path=test_csv,
        batch_size=batch_size,
        force_extract=force_extract,
    )

    # Step 2: Pre-calibration baseline metrics (T = 1.0)
    val_metrics_pre = evaluate_metrics(
        val_logits, val_labels, temperature=1.0, rejection_threshold=rejection_threshold
    )
    test_metrics_pre = evaluate_metrics(
        test_logits, test_labels, temperature=1.0, rejection_threshold=rejection_threshold
    )

    logger.info(
        f"[{crop} Pre-Calibration (T=1.0)]\n"
        f"  Val  -> ECE: {val_metrics_pre['ece']:.4f} | NLL: {val_metrics_pre['nll']:.4f} | "
        f"Brier: {val_metrics_pre['brier_score']:.4f} | Acc: {val_metrics_pre['accuracy']:.4f} | "
        f"F1: {val_metrics_pre['macro_f1']:.4f} | MeanConf: {val_metrics_pre['mean_confidence']:.4f} | "
        f"Rejection: {val_metrics_pre['rejection_rate']*100:.2f}%\n"
        f"  Test -> ECE: {test_metrics_pre['ece']:.4f} | NLL: {test_metrics_pre['nll']:.4f} | "
        f"Brier: {test_metrics_pre['brier_score']:.4f} | Acc: {test_metrics_pre['accuracy']:.4f} | "
        f"F1: {test_metrics_pre['macro_f1']:.4f} | MeanConf: {test_metrics_pre['mean_confidence']:.4f} | "
        f"Rejection: {test_metrics_pre['rejection_rate']*100:.2f}%"
    )

    # Step 3: Fit T on validation split ONLY
    optimal_T = fit_temperature(val_logits, val_labels)

    # Step 4: Post-calibration metrics (T = optimal_T)
    val_metrics_post = evaluate_metrics(
        val_logits, val_labels, temperature=optimal_T, rejection_threshold=rejection_threshold
    )
    test_metrics_post = evaluate_metrics(
        test_logits, test_labels, temperature=optimal_T, rejection_threshold=rejection_threshold
    )

    logger.info(
        f"[{crop} Post-Calibration (T={optimal_T:.4f})]\n"
        f"  Val  -> ECE: {val_metrics_post['ece']:.4f} (Δ {val_metrics_post['ece'] - val_metrics_pre['ece']:+.4f}) | "
        f"NLL: {val_metrics_post['nll']:.4f} (Δ {val_metrics_post['nll'] - val_metrics_pre['nll']:+.4f}) | "
        f"Brier: {val_metrics_post['brier_score']:.4f} | Acc: {val_metrics_post['accuracy']:.4f} | "
        f"F1: {val_metrics_post['macro_f1']:.4f} | MeanConf: {val_metrics_post['mean_confidence']:.4f} | "
        f"Rejection: {val_metrics_post['rejection_rate']*100:.2f}%\n"
        f"  Test -> ECE: {test_metrics_post['ece']:.4f} (Δ {test_metrics_post['ece'] - test_metrics_pre['ece']:+.4f}) | "
        f"NLL: {test_metrics_post['nll']:.4f} (Δ {test_metrics_post['nll'] - test_metrics_pre['nll']:+.4f}) | "
        f"Brier: {test_metrics_post['brier_score']:.4f} | Acc: {test_metrics_post['accuracy']:.4f} | "
        f"F1: {test_metrics_post['macro_f1']:.4f} | MeanConf: {test_metrics_post['mean_confidence']:.4f} | "
        f"Rejection: {test_metrics_post['rejection_rate']*100:.2f}%"
    )

    # Step 5: Assert Invariance (Argmax unchanged, Accuracy and F1 identical)
    val_preds_pre = np.argmax(val_logits, axis=1)
    val_preds_post = np.argmax(val_logits / optimal_T, axis=1)
    assert np.array_equal(val_preds_pre, val_preds_post), "Val predictions changed under temperature scaling!"

    test_preds_pre = np.argmax(test_logits, axis=1)
    test_preds_post = np.argmax(test_logits / optimal_T, axis=1)
    assert np.array_equal(test_preds_pre, test_preds_post), "Test predictions changed under temperature scaling!"

    assert np.isclose(val_metrics_pre["accuracy"], val_metrics_post["accuracy"], atol=1e-7), "Val accuracy changed!"
    assert np.isclose(val_metrics_pre["macro_f1"], val_metrics_post["macro_f1"], atol=1e-7), "Val Macro F1 changed!"
    assert np.isclose(test_metrics_pre["accuracy"], test_metrics_post["accuracy"], atol=1e-7), "Test accuracy changed!"
    assert np.isclose(test_metrics_pre["macro_f1"], test_metrics_post["macro_f1"], atol=1e-7), "Test Macro F1 changed!"

    logger.info("✓ Prediction invariance verified: argmax, accuracy, and Macro F1 are strictly preserved.")

    # Step 6: Save crop-specific temperature artifact
    CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)
    temp_artifact_path = CALIBRATION_DIR / f"{crop}_temperature.json"
    temp_artifact_data = {
        "crop": crop,
        "model_architecture": config.architecture,
        "seed": config.seed,
        "img_size": config.img_size,
        "num_classes": config.num_classes,
        "classes": classes,
        "temperature": round(optimal_T, 6),
        "optimization_method": "L-BFGS on validation Negative Log Likelihood",
        "optimization_split": f"{crop}_val.csv (N={len(val_labels)})",
        "evaluation_split": f"{crop}_test.csv (N={len(test_labels)})",
        "default_rejection_threshold": rejection_threshold,
        "val_metrics": {
            "pre": val_metrics_pre,
            "post": val_metrics_post,
        },
        "test_metrics": {
            "pre": test_metrics_pre,
            "post": test_metrics_post,
        },
        "calibrated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    with open(temp_artifact_path, "w", encoding="utf-8") as f:
        json.dump(temp_artifact_data, f, indent=2)
    logger.info(f"✓ Saved temperature artifact to {temp_artifact_path}")

    return {
        "crop": crop,
        "temperature": optimal_T,
        "val_pre": val_metrics_pre,
        "val_post": val_metrics_post,
        "test_pre": test_metrics_pre,
        "test_post": test_metrics_post,
        "artifact_path": str(temp_artifact_path),
    }


def generate_overall_reports(results: Dict[str, Dict[str, Any]]):
    """
    Combines single-crop calibration results into comprehensive
    calibration_report.json and reliability_data.json.
    """
    CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)

    # 1. calibration_report.json
    report_data = {
        "title": "DRISHYA Step A: Trustworthy Confidence Calibration Report",
        "methodology": "Post-Hoc Temperature Scaling (Guo et al., 2017) via L-BFGS on validation NLL",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "crops": {},
    }

    reliability_data = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "crops": {},
    }

    for crop, res in results.items():
        report_data["crops"][crop] = {
            "temperature": round(res["temperature"], 6),
            "validation_split": {
                "n_samples": res["val_pre"]["num_samples"],
                "ece_before": res["val_pre"]["ece"],
                "ece_after": res["val_post"]["ece"],
                "ece_reduction_percent": round((res["val_pre"]["ece"] - res["val_post"]["ece"]) / max(res["val_pre"]["ece"], 1e-6) * 100, 2),
                "nll_before": res["val_pre"]["nll"],
                "nll_after": res["val_post"]["nll"],
                "brier_before": res["val_pre"]["brier_score"],
                "brier_after": res["val_post"]["brier_score"],
                "accuracy": res["val_post"]["accuracy"],
                "macro_f1": res["val_post"]["macro_f1"],
                "mean_confidence_before": res["val_pre"]["mean_confidence"],
                "mean_confidence_after": res["val_post"]["mean_confidence"],
                "rejection_rate_before": res["val_pre"]["rejection_rate"],
                "rejection_rate_after": res["val_post"]["rejection_rate"],
            },
            "test_split": {
                "n_samples": res["test_pre"]["num_samples"],
                "ece_before": res["test_pre"]["ece"],
                "ece_after": res["test_post"]["ece"],
                "ece_reduction_percent": round((res["test_pre"]["ece"] - res["test_post"]["ece"]) / max(res["test_pre"]["ece"], 1e-6) * 100, 2),
                "nll_before": res["test_pre"]["nll"],
                "nll_after": res["test_post"]["nll"],
                "brier_before": res["test_pre"]["brier_score"],
                "brier_after": res["test_post"]["brier_score"],
                "accuracy": res["test_post"]["accuracy"],
                "macro_f1": res["test_post"]["macro_f1"],
                "mean_confidence_before": res["test_pre"]["mean_confidence"],
                "mean_confidence_after": res["test_post"]["mean_confidence"],
                "rejection_rate_before": res["test_pre"]["rejection_rate"],
                "rejection_rate_after": res["test_post"]["rejection_rate"],
            },
        }

        reliability_data["crops"][crop] = {
            "validation": {
                "uncalibrated_bins": res["val_pre"]["bins"],
                "calibrated_bins": res["val_post"]["bins"],
            },
            "test": {
                "uncalibrated_bins": res["test_pre"]["bins"],
                "calibrated_bins": res["test_post"]["bins"],
            },
        }

    report_path = CALIBRATION_DIR / "calibration_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    logger.info(f"✓ Saved calibration summary report to {report_path}")

    reliability_path = CALIBRATION_DIR / "reliability_data.json"
    with open(reliability_path, "w", encoding="utf-8") as f:
        json.dump(reliability_data, f, indent=2)
    logger.info(f"✓ Saved reliability diagram data to {reliability_path}")


def main():
    parser = argparse.ArgumentParser(description="DRISHYA Confidence Calibration Pipeline")
    parser.add_argument("--crop", choices=["turmeric", "citrus", "all"], default="all", help="Crop to calibrate")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for logit extraction")
    parser.add_argument("--force-extract", action="store_true", help="Force re-extraction of logits bypassing cache")
    parser.add_argument("--threshold", type=float, default=0.65, help="Rejection safety threshold")
    args = parser.parse_args()

    crops = ["turmeric", "citrus"] if args.crop == "all" else [args.crop]
    results = {}

    for crop in crops:
        res = calibrate_crop(
            crop=crop,
            batch_size=args.batch_size,
            force_extract=args.force_extract,
            rejection_threshold=args.threshold,
        )
        results[crop] = res

    # If both or existing saved artifacts, generate overall reports
    # Check if the other crop exists on disk so we can generate full combined report
    for other_crop in ["turmeric", "citrus"]:
        if other_crop not in results:
            other_json = CALIBRATION_DIR / f"{other_crop}_temperature.json"
            if other_json.exists():
                with open(other_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    results[other_crop] = {
                        "crop": other_crop,
                        "temperature": data["temperature"],
                        "val_pre": data["val_metrics"]["pre"],
                        "val_post": data["val_metrics"]["post"],
                        "test_pre": data["test_metrics"]["pre"],
                        "test_post": data["test_metrics"]["post"],
                    }

    generate_overall_reports(results)
    logger.info("\nCalibration pipeline completed successfully.")


if __name__ == "__main__":
    main()
