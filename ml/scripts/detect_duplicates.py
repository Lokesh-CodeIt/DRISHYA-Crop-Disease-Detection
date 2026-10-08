#!/usr/bin/env python3
"""
detect_duplicates.py - LeafLens Image Deduplication Pipeline

Purpose:
    Identifies exact and near-duplicate images within and between datasets.
    Crucial for preventing data leakage across training, validation, and test splits,
    as well as cross-dataset validation benchmarks.

Methodology:
    1. Exact duplicates: SHA-256 cryptographic hashing.
    2. Near duplicates: Perceptual difference hashing (dHash) computed across grayscale resized thumbnails.

Usage:
    python ml/scripts/detect_duplicates.py --data-dir ml/datasets/cleaned/turmeric --crop turmeric
"""

import argparse
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
from PIL import Image
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LeafLens.Duplicates")

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_dhash(image_path: Path, hash_size: int = 8) -> int:
    """Computes difference hash (dHash) of an image using pure PIL and numpy."""
    with Image.open(image_path) as img:
        img_gray = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = np.array(img_gray, dtype=np.int32)
        diff = pixels[:, 1:] > pixels[:, :-1]
        # Pack boolean array into an integer bitmask
        decimal_val = 0
        for bit in diff.flatten():
            decimal_val = (decimal_val << 1) | int(bit)
        return decimal_val


def hamming_distance(hash1: int, hash2: int) -> int:
    """Computes bitwise Hamming distance between two integers."""
    return bin(hash1 ^ hash2).count("1")


def scan_duplicates(data_dir: Path, max_hamming_dist: int = 2) -> Dict[str, Any]:
    """Scans directory for exact and near-duplicate images."""
    image_paths = [p for p in data_dir.rglob("*") if p.suffix.lower() in VALID_EXTENSIONS]
    logger.info(f"Scanning {len(image_paths)} images in {data_dir} for duplicates...")

    # Exact duplicates via SHA256
    exact_hash_map: Dict[str, List[str]] = defaultdict(list)
    dhash_map: Dict[str, int] = {}

    for path in image_paths:
        try:
            sha = compute_sha256(path)
            exact_hash_map[sha].append(str(path))
            dhash_map[str(path)] = compute_dhash(path)
        except Exception as e:
            logger.warning(f"Error reading image {path}: {e}")

    exact_duplicates = [paths for paths in exact_hash_map.values() if len(paths) > 1]

    # Near duplicates via dHash comparison
    near_duplicates: List[Dict[str, Any]] = []
    items = list(dhash_map.items())
    for i in range(len(items)):
        path_a, hash_a = items[i]
        for j in range(i + 1, len(items)):
            path_b, hash_b = items[j]
            dist = hamming_distance(hash_a, hash_b)
            if dist <= max_hamming_dist:
                near_duplicates.append({
                    "image_a": path_a,
                    "image_b": path_b,
                    "hamming_distance": dist,
                })

    return {
        "dataset_path": str(data_dir),
        "total_images_scanned": len(image_paths),
        "exact_duplicate_groups": len(exact_duplicates),
        "exact_duplicate_files": sum(len(g) - 1 for g in exact_duplicates),
        "exact_duplicates": exact_duplicates,
        "near_duplicate_pairs": len(near_duplicates),
        "near_duplicates": near_duplicates[:50],  # Sample first 50
    }


def main():
    parser = argparse.ArgumentParser(description="Detect exact and near-duplicate images.")
    parser.add_argument("--data-dir", type=str, required=True, help="Image directory to scan.")
    parser.add_argument("--crop", type=str, default="generic", help="Crop name.")
    parser.add_argument("--max-hamming-dist", type=int, default=2, help="Max Hamming distance for near duplicates.")
    parser.add_argument("--output-report", type=str, default=None, help="Output report path.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    report = scan_duplicates(data_dir, max_hamming_dist=args.max_hamming_dist)

    out_file = args.output_report
    if not out_file:
        out_dir = Path("data/reports")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"duplicates_{args.crop}_{data_dir.name}.json"
    else:
        out_file = Path(out_file)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Duplicate scan complete. Exact groups: {report['exact_duplicate_groups']}, Near pairs: {report['near_duplicate_pairs']}. Written to {out_file}")


if __name__ == "__main__":
    main()
