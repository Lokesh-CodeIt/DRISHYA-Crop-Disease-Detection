#!/usr/bin/env python3
"""
clean_datasets.py - LeafLens Non-Destructive Dataset Cleaning Pipeline

Purpose:
    Performs safe, reproducible cleaning of verified raw images.
    - Preserves raw images completely (NEVER modifies or deletes originals).
    - Standardizes images into RGB mode (properly handling transparency channels).
    - Writes cleaned images to ml/datasets/cleaned/<crop>/ preserving class hierarchy.
    - Generates provenance metadata mapping source file paths and cryptographic hashes (SHA-256)
      to cleaned destination files in data/metadata/.

Usage:
    python ml/scripts/clean_datasets.py --source-dir ml/datasets/raw/turmeric --dest-dir ml/datasets/cleaned/turmeric --crop turmeric
"""

import argparse
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LeafLens.Clean")

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def compute_sha256(file_path: Path) -> str:
    """Computes SHA-256 hash of a file for provenance verification."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def clean_dataset(source_dir: Path, dest_dir: Path, crop: str) -> Dict[str, Any]:
    """Cleans images from source_dir into dest_dir non-destructively."""
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    dest_dir.mkdir(parents=True, exist_ok=True)
    manifest_records: List[Dict[str, Any]] = []
    classes_count: Dict[str, int] = {}
    total_processed = 0
    total_skipped = 0

    subdirs = [d for d in source_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]

    for class_dir in sorted(subdirs):
        class_name = class_dir.name
        out_class_dir = dest_dir / class_name
        out_class_dir.mkdir(parents=True, exist_ok=True)

        img_files = [f for f in class_dir.rglob("*") if f.suffix.lower() in VALID_EXTENSIONS]
        valid_in_class = 0

        for img_path in img_files:
            try:
                with Image.open(img_path) as img:
                    img.load()
                    # Convert to RGB mode
                    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                        # Convert transparent to RGB with white background
                        alpha_img = img.convert("RGBA")
                        canvas = Image.new("RGB", alpha_img.size, (255, 255, 255))
                        canvas.paste(alpha_img, mask=alpha_img.split()[3])
                        cleaned_img = canvas
                    else:
                        cleaned_img = img.convert("RGB")

                    # Output filename standardized as .jpg with source stem
                    out_filename = f"{img_path.stem}.jpg"
                    out_path = out_class_dir / out_filename
                    cleaned_img.save(out_path, format="JPEG", quality=95)

                src_hash = compute_sha256(img_path)
                dst_hash = compute_sha256(out_path)

                manifest_records.append({
                    "crop": crop,
                    "class": class_name,
                    "source_path": str(img_path.resolve()),
                    "cleaned_path": str(out_path.resolve()),
                    "source_sha256": src_hash,
                    "cleaned_sha256": dst_hash,
                    "width": cleaned_img.width,
                    "height": cleaned_img.height,
                })
                valid_in_class += 1
                total_processed += 1

            except Exception as e:
                logger.warning(f"Skipping corrupted file {img_path}: {e}")
                total_skipped += 1

        classes_count[class_name] = valid_in_class

    return {
        "crop": crop,
        "source_dir": str(source_dir),
        "dest_dir": str(dest_dir),
        "total_processed": total_processed,
        "total_skipped": total_skipped,
        "classes": classes_count,
        "manifest": manifest_records,
    }


def main():
    parser = argparse.ArgumentParser(description="Clean raw image datasets into standardized RGB format.")
    parser.add_argument("--source-dir", type=str, required=True, help="Raw data directory.")
    parser.add_argument("--dest-dir", type=str, required=True, help="Cleaned output directory.")
    parser.add_argument("--crop", type=str, required=True, choices=["turmeric", "citrus", "generic"])
    parser.add_argument("--metadata-dir", type=str, default="data/metadata", help="Metadata output folder.")
    args = parser.parse_args()

    source = Path(args.source_dir)
    dest = Path(args.dest_dir)
    logger.info(f"Cleaning dataset from {source} to {dest} for {args.crop}")

    result = clean_dataset(source, dest, args.crop)

    # Save provenance metadata
    meta_dir = Path(args.metadata_dir)
    meta_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = meta_dir / f"provenance_cleaned_{args.crop}_{dest.name}.json"

    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    logger.info(f"Cleaning finished. Processed: {result['total_processed']}, Skipped: {result['total_skipped']}. Provenance saved to {manifest_file}")


if __name__ == "__main__":
    main()
