#!/usr/bin/env python3
"""
inspect_datasets.py - LeafLens Dataset Inspection Script

Purpose:
    Performs non-destructive inspection of dataset directories for Turmeric and Citrus crops.
    Validates image readability, format consistency, dimensions, color channels, and class distributions.
    Outputs structured JSON/Markdown reports to data/reports/ and metadata to data/metadata/.

Safety Rules:
    - Strictly read-only: never modifies, deletes, or moves original dataset files.
    - Preserves dataset provenance.
    - Does not fabricate statistics; reports only on actual discovered files.

Usage:
    python ml/scripts/inspect_datasets.py --data-dir ml/datasets/raw/turmeric --crop turmeric
    python ml/scripts/inspect_datasets.py --data-dir ml/datasets/raw/citrus --crop citrus
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from collections import Counter
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LeafLens.Inspect")

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def inspect_dataset_directory(data_path: Path, crop: str) -> Dict[str, Any]:
    """Inspects an image dataset directory organized in class subfolders."""
    if not data_path.exists():
        logger.warning(f"Data directory does not exist: {data_path}")
        return {
            "crop": crop,
            "status": "directory_not_found",
            "path": str(data_path),
            "total_images": 0,
            "classes": {}
        }

    classes: Dict[str, Dict[str, Any]] = {}
    total_images = 0
    corrupted_files: List[str] = []
    dimensions: List[str] = []
    channel_counts: Counter = Counter()

    # Discover subdirectories as classes
    subdirs = [d for d in data_path.iterdir() if d.is_dir() and not d.name.startswith(".")]

    if not subdirs:
        logger.info(f"No subdirectories found in {data_path}. Checking flat directory...")
        # Flat directory check
        files = [f for f in data_path.iterdir() if f.suffix.lower() in VALID_EXTENSIONS]
        return {
            "crop": crop,
            "status": "flat_directory",
            "path": str(data_path),
            "total_images": len(files),
            "classes": {"uncategorized": {"count": len(files)}}
        }

    for class_dir in sorted(subdirs):
        class_name = class_dir.name
        img_files = [f for f in class_dir.rglob("*") if f.suffix.lower() in VALID_EXTENSIONS]
        valid_in_class = 0
        corrupted_in_class = 0

        for img_path in img_files:
            try:
                with Image.open(img_path) as img:
                    img.verify()  # Fast integrity check
                # Reopen to check dimensions and mode after verify() closes
                with Image.open(img_path) as img:
                    dimensions.append(f"{img.width}x{img.height}")
                    channel_counts[img.mode] += 1
                valid_in_class += 1
            except Exception as e:
                corrupted_in_class += 1
                corrupted_files.append(str(img_path.relative_to(data_path)))
                logger.error(f"Corrupt image {img_path}: {e}")

        classes[class_name] = {
            "total_files": len(img_files),
            "valid_images": valid_in_class,
            "corrupted_images": corrupted_in_class,
        }
        total_images += valid_in_class

    summary: Dict[str, Any] = {
        "crop": crop,
        "status": "inspected",
        "dataset_root": str(data_path),
        "total_valid_images": total_images,
        "total_classes": len(classes),
        "class_breakdown": classes,
        "color_modes": dict(channel_counts),
        "total_corrupted": len(corrupted_files),
        "corrupted_files_sample": corrupted_files[:20],
    }

    return summary


def main():
    parser = argparse.ArgumentParser(description="Inspect crop leaf image datasets.")
    parser.add_argument("--data-dir", type=str, required=True, help="Path to dataset directory.")
    parser.add_argument("--crop", type=str, choices=["turmeric", "citrus", "generic"], default="generic", help="Crop type.")
    parser.add_argument("--output-report", type=str, default=None, help="Optional output JSON report path.")
    args = parser.parse_args()

    data_path = Path(args.data_dir)
    logger.info(f"Starting inspection for crop: {args.crop} at {data_path}")

    report = inspect_dataset_directory(data_path, args.crop)

    out_file = args.output_report
    if not out_file:
        out_dir = Path("data/reports")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"inspection_{args.crop}_{data_path.name}.json"
    else:
        out_file = Path(out_file)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Inspection complete. Total valid: {report.get('total_valid_images', 0)}. Report written to {out_file}")


if __name__ == "__main__":
    main()
