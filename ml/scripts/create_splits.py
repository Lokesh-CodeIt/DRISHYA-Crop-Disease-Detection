#!/usr/bin/env python3
"""
create_splits.py - LeafLens Stratified Dataset Splitting Pipeline

Purpose:
    Generates reproducible train, validation, and test splits with class stratification.
    Exports split manifests as JSON/CSV in ml/datasets/splits/<crop>/ and reports split
    distribution to data/reports/.

Safety & Provenance:
    - Never moves or copies files; operates on relative file paths to keep raw/cleaned data intact.
    - Uses deterministic pseudo-random seeds.
    - Prevents data leakage.

Usage:
    python ml/scripts/create_splits.py --data-dir ml/datasets/cleaned/turmeric --crop turmeric --train-ratio 0.70 --val-ratio 0.15 --test-ratio 0.15 --seed 42
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LeafLens.Splits")

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def generate_stratified_splits(
    data_dir: Path,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
) -> Dict[str, Any]:
    """Generates stratified splits by class."""
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Ratios must sum to 1.0"
    rng = np.random.default_rng(seed)

    subdirs = [d for d in data_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    if not subdirs:
        raise ValueError(f"No class subdirectories found in {data_dir}")

    splits: Dict[str, List[Dict[str, str]]] = {"train": [], "val": [], "test": []}
    class_stats: Dict[str, Dict[str, int]] = {}

    for class_dir in sorted(subdirs):
        class_name = class_dir.name
        img_paths = sorted([p for p in class_dir.rglob("*") if p.suffix.lower() in VALID_EXTENSIONS])
        n_total = len(img_paths)

        if n_total == 0:
            logger.warning(f"Class '{class_name}' has 0 valid images. Skipping.")
            continue

        indices = np.arange(n_total)
        rng.shuffle(indices)

        n_train = int(np.floor(train_ratio * n_total))
        n_val = int(np.floor(val_ratio * n_total))
        # Ensure remaining go to test
        n_test = n_total - n_train - n_val

        train_idx = indices[:n_train]
        val_idx = indices[n_train:n_train + n_val]
        test_idx = indices[n_train + n_val:]

        for idx in train_idx:
            splits["train"].append({"path": str(img_paths[idx]), "class": class_name})
        for idx in val_idx:
            splits["val"].append({"path": str(img_paths[idx]), "class": class_name})
        for idx in test_idx:
            splits["test"].append({"path": str(img_paths[idx]), "class": class_name})

        class_stats[class_name] = {
            "total": n_total,
            "train": len(train_idx),
            "val": len(val_idx),
            "test": len(test_idx),
        }

    return {
        "dataset_dir": str(data_dir),
        "seed": seed,
        "ratios": {"train": train_ratio, "val": val_ratio, "test": test_ratio},
        "summary": {
            "total_images": sum(c["total"] for c in class_stats.values()),
            "train_images": len(splits["train"]),
            "val_images": len(splits["val"]),
            "test_images": len(splits["test"]),
        },
        "class_distributions": class_stats,
        "splits": splits,
    }


def main():
    parser = argparse.ArgumentParser(description="Create stratified train/val/test splits.")
    parser.add_argument("--data-dir", type=str, required=True, help="Cleaned image directory.")
    parser.add_argument("--crop", type=str, required=True, choices=["turmeric", "citrus", "generic"])
    parser.add_argument("--train-ratio", type=float, default=0.70, help="Train split fraction.")
    parser.add_argument("--val-ratio", type=float, default=0.15, help="Validation split fraction.")
    parser.add_argument("--test-ratio", type=float, default=0.15, help="Test split fraction.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument("--output-dir", type=str, default=None, help="Output splits directory.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    splits_data = generate_stratified_splits(
        data_dir=data_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
    )

    out_dir = Path(args.output_dir) if args.output_dir else Path(f"ml/datasets/splits/{args.crop}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save split manifests
    for split_name in ["train", "val", "test"]:
        split_file = out_dir / f"{split_name}.json"
        with open(split_file, "w", encoding="utf-8") as f:
            json.dump(splits_data["splits"][split_name], f, indent=2)

    # Save metadata summary
    report_file = Path("data/reports") / f"splits_{args.crop}_summary.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    summary_report = {k: v for k, v in splits_data.items() if k != "splits"}

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2)

    logger.info(f"Splits generated successfully for {args.crop} in {out_dir}. Summary written to {report_file}")


if __name__ == "__main__":
    main()
