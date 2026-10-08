#!/usr/bin/env python3
"""
build_colab_zip.py — Build CROP_DETECTION_COLAB_READY.zip for Google Colab migration
"""

import os
import sys
import time
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
OUT_DIR = PROJECT_ROOT / "COLAB_MIGRATION"
OUT_DIR.mkdir(parents=True, exist_ok=True)
ZIP_PATH = OUT_DIR / "CROP_DETECTION_COLAB_READY.zip"

# Required 4 dataset zip archives
REQUIRED_DATASETS = [
    "A Citrus Fruits and Leaves Dataset for Detection and Classification of Citrus Diseases through Machine Learning.zip",
    "Image Dataset for Turmeric Plant Leaf Disease Detection.zip",
    "Large-Scale Lemon Leaf Disease and Pest Image Data.zip",
    "Turmeric Plant Disease Dataset Advancing AI for Agricultural Sustainability.zip",
]

def collect_files():
    """Collect (local_abs_path, arcname) for all files to be included."""
    files_to_add = []

    # 1. Root configuration / documentation / scripts
    root_files = [
        "requirements.txt",
        "colab_setup.py",
        "COLAB_TRAINING_NOTEBOOK.ipynb",
        "README_COLAB.md",
    ]
    for rf in root_files:
        p = PROJECT_ROOT / rf
        if p.exists():
            files_to_add.append((p, f"CROP_DETECTION/{rf}"))
        else:
            print(f"WARNING: Root file missing: {rf}")

    # 2. DATASET/ (Only the 4 referenced ZIPs)
    dataset_dir = PROJECT_ROOT / "DATASET"
    for dz in REQUIRED_DATASETS:
        p = dataset_dir / dz
        if p.exists():
            files_to_add.append((p, f"CROP_DETECTION/DATASET/{dz}"))
        else:
            raise FileNotFoundError(f"Required dataset ZIP missing: {p}")

    # 3. data/metadata/ and data/metadata/splits/
    meta_dir = PROJECT_ROOT / "data" / "metadata"
    for item in meta_dir.rglob("*"):
        if item.is_file() and not item.name.startswith("."):
            rel = item.relative_to(PROJECT_ROOT).as_posix()
            files_to_add.append((item, f"CROP_DETECTION/{rel}"))

    # 4. ml/ (scripts, configs, datasets, excluding experiments, checkpoints, caches)
    ml_dir = PROJECT_ROOT / "ml"
    exclude_dirs = {"experiments", "checkpoints", "__pycache__", ".pytest_cache"}
    for item in ml_dir.rglob("*"):
        if item.is_file() and not item.name.startswith("."):
            # Check if any parent part is in exclude_dirs
            rel_parts = item.relative_to(ml_dir).parts
            if any(part in exclude_dirs for part in rel_parts):
                continue
            if item.suffix in [".pyc", ".pt", ".pth", ".log"]:
                continue
            rel = item.relative_to(PROJECT_ROOT).as_posix()
            files_to_add.append((item, f"CROP_DETECTION/{rel}"))

    # 5. docs/
    docs_dir = PROJECT_ROOT / "docs"
    if docs_dir.exists():
        for item in docs_dir.rglob("*"):
            if item.is_file() and not item.name.startswith("."):
                rel = item.relative_to(PROJECT_ROOT).as_posix()
                files_to_add.append((item, f"CROP_DETECTION/{rel}"))

    return files_to_add


def main():
    print("=" * 70)
    print("BUILDING COLAB MIGRATION ZIP")
    print(f"Target: {ZIP_PATH}")
    print("=" * 70)

    files = collect_files()
    print(f"Collected {len(files)} files to package:")

    datasets_count = 0
    splits_count = 0
    scripts_count = 0
    other_count = 0

    for src, arc in files:
        size_mb = src.stat().st_size / (1024**2)
        if "DATASET" in arc and arc.endswith(".zip"):
            datasets_count += 1
            print(f"  [DATASET] {arc} ({size_mb:.1f} MB)")
        elif "splits" in arc:
            splits_count += 1
            print(f"  [SPLIT]   {arc} ({size_mb:.2f} MB)")
        elif "ml/scripts" in arc:
            scripts_count += 1
            print(f"  [SCRIPT]  {arc}")
        else:
            other_count += 1
            print(f"  [OTHER]   {arc}")

    print("-" * 70)
    print(f"Summary: {datasets_count} datasets, {splits_count} splits, {scripts_count} scripts, {other_count} configs/docs/root.")
    print("-" * 70)

    t0 = time.time()
    print("Creating ZIP archive (allowZip64=True)...")

    # If file exists, remove to start clean
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(ZIP_PATH, "w", allowZip64=True) as zf:
        for i, (src, arc) in enumerate(files, 1):
            # Already compressed ZIP files: use ZIP_STORED to avoid re-compression overhead
            if src.suffix.lower() == ".zip":
                compress = zipfile.ZIP_STORED
            else:
                compress = zipfile.ZIP_DEFLATED

            print(f"[{i}/{len(files)}] Adding {arc} ...", flush=True)
            zf.write(src, arcname=arc, compress_type=compress)

    elapsed = time.time() - t0
    final_size_bytes = ZIP_PATH.stat().st_size
    final_size_gb = final_size_bytes / (1024**3)

    print("=" * 70)
    print("ZIP CREATION COMPLETE!")
    print(f"Path:       {ZIP_PATH}")
    print(f"Size:       {final_size_bytes:,} bytes ({final_size_gb:.2f} GB)")
    print(f"Total time: {elapsed:.1f}s")
    print("=" * 70)

    # Verification of created ZIP
    print("\nVerifying archive integrity (reading central directory)...")
    with zipfile.ZipFile(ZIP_PATH, "r") as test_zf:
        infolist = test_zf.infolist()
        print(f"Verification: Successfully read {len(infolist)} entries in archive.")

if __name__ == "__main__":
    main()
