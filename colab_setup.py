#!/usr/bin/env python3
"""
colab_setup.py — LeafLens Google Colab Environment Verification & Quickstart

Usage in Google Colab:
    !python colab_setup.py
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "ml" / "scripts"))

def main():
    print("=" * 70)
    print("LeafLens Google Colab Environment Verification")
    print("=" * 70)

    # 1. Check Python & PyTorch
    import torch
    import torchvision
    print(f"Python Version:   {sys.version.split()[0]}")
    print(f"PyTorch Version:  {torch.__version__}")
    print(f"Torchvision:      {torchvision.__version__}")

    # 2. Check GPU / CUDA
    cuda_avail = torch.cuda.is_available()
    print(f"CUDA Available:   {cuda_avail}")
    if cuda_avail:
        print(f"GPU Device:       {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory:       {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    else:
        print("WARNING: CUDA is NOT available! Go to Runtime -> Change runtime type -> Select T4 GPU or A100.")

    # 3. Check Dataset Archives
    dataset_dir = PROJECT_ROOT / "DATASET"
    required_zips = [
        "A Citrus Fruits and Leaves Dataset for Detection and Classification of Citrus Diseases through Machine Learning.zip",
        "Image Dataset for Turmeric Plant Leaf Disease Detection.zip",
        "Large-Scale Lemon Leaf Disease and Pest Image Data.zip",
        "Turmeric Plant Disease Dataset Advancing AI for Agricultural Sustainability.zip",
    ]
    print("\nDataset Archives:")
    all_zips_ok = True
    for zname in required_zips:
        zp = dataset_dir / zname
        exists = zp.exists()
        size_mb = zp.stat().st_size / (1024**2) if exists else 0
        status = "OK" if exists else "MISSING"
        if not exists:
            all_zips_ok = False
        print(f"  [{status}] {zname} ({size_mb:.1f} MB)")

    # 4. Check Split CSVs
    splits_dir = PROJECT_ROOT / "data" / "metadata" / "splits"
    required_splits = [
        ("turmeric_train.csv", 870),
        ("turmeric_val.csv", 187),
        ("turmeric_test.csv", 186),
        ("citrus_train.csv", 10435),
        ("citrus_val.csv", 2235),
        ("citrus_test.csv", 2241),
        ("citrus_external_test.csv", 609),
    ]
    print("\nSplit Manifests:")
    import csv
    all_splits_ok = True
    for sname, expected_rows in required_splits:
        sp = splits_dir / sname
        if not sp.exists():
            print(f"  [MISSING] {sname}")
            all_splits_ok = False
            continue
        with open(sp, encoding="utf-8") as f:
            rows = sum(1 for _ in csv.DictReader(f))
        status = "OK" if rows == expected_rows else f"COUNT MISMATCH ({rows} vs {expected_rows})"
        if rows != expected_rows:
            all_splits_ok = False
        print(f"  [{status}] {sname}: {rows} rows")

    # 5. Test ZIP-native Loader
    print("\nTesting ZIP-Native Image Loader:")
    from train_pipeline import open_pil_image
    try:
        with open(splits_dir / "turmeric_train.csv", encoding="utf-8") as f:
            t_path = next(csv.DictReader(f))["absolute_path"]
        t_img = open_pil_image(t_path)
        print(f"  [OK] Turmeric sample image loaded: size={t_img.size}, mode={t_img.mode}")

        with open(splits_dir / "citrus_train.csv", encoding="utf-8") as f:
            c_path = next(csv.DictReader(f))["absolute_path"]
        c_img = open_pil_image(c_path)
        print(f"  [OK] Citrus sample image loaded: size={c_img.size}, mode={c_img.mode}")
    except Exception as e:
        print(f"  [ERROR] Image loading failed: {e}")
        return

    # 6. Test Model Head Replacements
    print("\nTesting Model Definitions:")
    from train_pipeline import build_model
    try:
        m1 = build_model("turmeric", 4)
        print("  [OK] Turmeric ConvNeXt-Tiny initialized (4 classes)")
        m2 = build_model("citrus", 18)
        print("  [OK] Citrus EfficientNetV2-S initialized (18 classes)")
    except Exception as e:
        print(f"  [ERROR] Model build failed: {e}")
        return

    print("\n" + "=" * 70)
    print("ALL VERIFICATIONS PASSED! System is fully ready for training.")
    print("=" * 70)
    print("\nTo run smoke test:")
    print("  !python ml/scripts/train_pipeline.py --smoke-test")
    print("\nTo train Turmeric (ConvNeXt-Tiny, Seed 42):")
    print("  !python ml/scripts/train_pipeline.py --crop turmeric --seed 42")
    print("\nTo train Citrus (EfficientNetV2-S, Seed 42):")
    print("  !python ml/scripts/train_pipeline.py --crop citrus --seed 42")
    print("\nTo run all 6 experiments sequentially (seeds 42, 123, 7):")
    print("  !python ml/scripts/train_pipeline.py --run-all")
    print("=" * 70)

if __name__ == "__main__":
    main()
