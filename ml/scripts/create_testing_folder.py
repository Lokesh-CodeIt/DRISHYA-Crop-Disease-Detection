"""
create_testing_folder.py
DRISHYA — safe website testing image folder creator.
Only COPIES images from existing ZIPs. Never moves/deletes originals.
"""
import sys, csv
from pathlib import Path

PROJECT_ROOT = Path(r".")
sys.path.insert(0, str(PROJECT_ROOT))

from ml.scripts.zip_image_reader import open_image_bytes
import pandas as pd

TESTING_DIR = PROJECT_ROOT / "TESTING"

TUR_CLASSES = {
    "Healthy":     "healthy",
    "Dry Leaf":    "dry_leaf",
    "Leaf Blotch": "leaf_blotch",
    "Leaf Spot":   "leaf_spot",
}

CIT_CLASSES = {
    "Algal_Leaf_Spot":   "algal_leaf_spot",
    "Anthracnose":       "anthracnose",
    "Bacterial Blight":  "bacterial_blight",
    "Black Spot":        "black_spot",
    "Citrus Canker":     "citrus_canker",
    "Citrus Hindu Mite": "citrus_hindu_mite",
    "Citrus Leafminer":  "citrus_leafminer",
    "Citrus_Pest":       "citrus_pest",
    "Citrus_Scab":       "citrus_scab",
    "Curl Leaf":         "curl_leaf",
    "Dry Leaf":          "dry_leaf",
    "Greening":          "greening",
    "Healthy":           "healthy",
    "Lemon_Sooty_Mold":  "lemon_sooty_mold",
    "Melanose":          "melanose",
    "Spider Mites":      "spider_mites",
    "Swallowtail Larval Herbivory (Deficiency)": "swallowtail_larval_herbivory_deficiency",
    "Yellow_Spot":       "yellow_spot",
}

# Edge-case images identified by metric scan (brightness / Laplacian / HSV analysis)
EDGE_IMGS = [
    # (category, prefix, virtual_zip_path, crop, expected_class, src_id, src_dataset)
    ("low_light",        "low_light",  "DATASET/Large-Scale Lemon Leaf Disease and Pest Image Data.zip#Large-Scale Lemon Leaf Disease and Pest Image Data/Algal_Leaf_Spot/Algal_Leaf_Spot_605.jpg",   "citrus",   "Algal_Leaf_Spot",  "CITRUS_LEMON_00605", "Large-Scale Lemon Leaf Disease and Pest Image Data"),
    ("low_light",        "low_light",  "DATASET/Large-Scale Lemon Leaf Disease and Pest Image Data.zip#Large-Scale Lemon Leaf Disease and Pest Image Data/Algal_Leaf_Spot/Algal_Leaf_Spot_753.jpg",   "citrus",   "Algal_Leaf_Spot",  "CITRUS_LEMON_00748", "Large-Scale Lemon Leaf Disease and Pest Image Data"),
    ("blurry",           "blurry",     "DATASET/Large-Scale Lemon Leaf Disease and Pest Image Data.zip#Large-Scale Lemon Leaf Disease and Pest Image Data/Black Spot/Black Spot_460.jpg",              "citrus",   "Black Spot",       "CITRUS_LEMON_02652", "Large-Scale Lemon Leaf Disease and Pest Image Data"),
    ("blurry",           "blurry",     "DATASET/Large-Scale Lemon Leaf Disease and Pest Image Data.zip#Large-Scale Lemon Leaf Disease and Pest Image Data/Curl Leaf/Curl Leaf_228.jpg",               "citrus",   "Curl Leaf",        "CITRUS_LEMON_08218", "Large-Scale Lemon Leaf Disease and Pest Image Data"),
    ("heavy_background", "heavy_bg",   "DATASET/Large-Scale Lemon Leaf Disease and Pest Image Data.zip#Large-Scale Lemon Leaf Disease and Pest Image Data/Curl Leaf/Curl Leaf_525.jpg",               "citrus",   "Curl Leaf",        "CITRUS_LEMON_08516", "Large-Scale Lemon Leaf Disease and Pest Image Data"),
    ("heavy_background", "heavy_bg",   "DATASET/Large-Scale Lemon Leaf Disease and Pest Image Data.zip#Large-Scale Lemon Leaf Disease and Pest Image Data/Citrus_Scab/Citrus_Scab_131.jpg",           "citrus",   "Citrus_Scab",      "CITRUS_LEMON_06935", "Large-Scale Lemon Leaf Disease and Pest Image Data"),
    ("poor_composition", "poor_comp",  "DATASET/Large-Scale Lemon Leaf Disease and Pest Image Data.zip#Large-Scale Lemon Leaf Disease and Pest Image Data/Citrus_Pest/Citrus_Pest_502.jpg",           "citrus",   "Citrus_Pest",      "CITRUS_LEMON_06761", "Large-Scale Lemon Leaf Disease and Pest Image Data"),
    ("non_leaf",         "non_leaf",   "DATASET/Turmeric Plant Disease Dataset Advancing AI for Agricultural Sustainability.zip#Turmeric Plant Disease Dataset Advancing AI for Agricultural Sustainability/Turmeric Plant Disease.zip#Turmeric Plant Disease/Rhizome Rot/Rhizome Rot00001.JPG",  "turmeric", "",  "TURM_04961",       "Turmeric Plant Disease Dataset Advancing AI (Original)"),
    ("non_leaf",         "non_leaf",   "DATASET/A Citrus Fruits and Leaves Dataset for Detection and Classification of Citrus Diseases through Machine Learning.zip#A Citrus Fruits and Leaves Dataset for Detection and Classification of Citrus Diseases through Machine Learning/Citrus Plant Dataset/Citrus.zip#Citrus/Fruits/Black spot/Black spot (1).jpg", "citrus",   "",  "CITRUS_SEC_00001", "A Citrus Fruits and Leaves Dataset for Detection and Classification of Citrus Diseases through Machine Learning"),
]


def save_img(vpath, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(open_image_bytes(vpath))


def pick3(df, col, val, seed=42):
    sub = df[df[col] == val]
    return sub.sample(min(3, len(sub)), random_state=seed)


def main():
    print("=" * 60)
    print("DRISHYA TESTING FOLDER CREATOR")
    print("=" * 60)

    t_test = pd.read_csv(PROJECT_ROOT / "data/metadata/splits/turmeric_test.csv")
    c_test = pd.read_csv(PROJECT_ROOT / "data/metadata/splits/citrus_test.csv")

    manifest_rows = []
    total = tur = cit = edge = 0
    skipped = []

    # ── Turmeric
    print("\n[TURMERIC]")
    for cls, fld in TUR_CLASSES.items():
        rows = pick3(t_test, "final_class", cls)
        if rows.empty:
            skipped.append("turmeric/" + cls)
            continue
        for i, (_, r) in enumerate(rows.iterrows(), 1):
            dest = TESTING_DIR / "turmeric" / fld / ("TUR_" + fld + "_" + str(i).zfill(2) + ".jpg")
            try:
                save_img(r["absolute_path"], dest)
                manifest_rows.append({
                    "test_id": "TUR_" + fld.upper() + "_" + str(i).zfill(3),
                    "crop": "turmeric",
                    "expected_class": cls,
                    "source_dataset": r["source_dataset"],
                    "source_path": r["absolute_path"],
                    "original_filename": r["absolute_path"].split("/")[-1],
                    "purpose": cls + " test image",
                })
                total += 1; tur += 1
                print("  OK " + dest.name + " <- " + r["image_id"])
            except Exception as e:
                print("  FAILED " + cls + " #" + str(i) + ": " + str(e))

    # ── Citrus
    print("\n[CITRUS]")
    for cls, fld in CIT_CLASSES.items():
        rows = pick3(c_test, "final_class", cls)
        if rows.empty:
            skipped.append("citrus/" + cls)
            continue
        for i, (_, r) in enumerate(rows.iterrows(), 1):
            dest = TESTING_DIR / "citrus" / fld / ("CIT_" + fld + "_" + str(i).zfill(2) + ".jpg")
            try:
                save_img(r["absolute_path"], dest)
                manifest_rows.append({
                    "test_id": "CIT_" + fld.upper() + "_" + str(i).zfill(3),
                    "crop": "citrus",
                    "expected_class": cls,
                    "source_dataset": r["source_dataset"],
                    "source_path": r["absolute_path"],
                    "original_filename": r["absolute_path"].split("/")[-1],
                    "purpose": cls + " test image",
                })
                total += 1; cit += 1
                print("  OK " + dest.name + " <- " + r["image_id"])
            except Exception as e:
                print("  FAILED " + cls + " #" + str(i) + ": " + str(e))

    # ── Edge cases
    print("\n[EDGE CASES]")
    cat_counters = {}
    for cat, prefix, vpath, crop, exp_cls, src_id, src_ds in EDGE_IMGS:
        cat_counters[cat] = cat_counters.get(cat, 0) + 1
        i = cat_counters[cat]
        dest = TESTING_DIR / "edge_cases" / cat / ("EDGE_" + prefix + "_" + str(i).zfill(2) + ".jpg")
        try:
            save_img(vpath, dest)
            manifest_rows.append({
                "test_id": "EDGE_" + prefix.upper() + "_" + str(i).zfill(3),
                "crop": crop if crop else "unknown",
                "expected_class": exp_cls,
                "source_dataset": src_ds,
                "source_path": vpath,
                "original_filename": vpath.split("/")[-1],
                "purpose": "edge_case/" + cat,
            })
            total += 1; edge += 1
            print("  OK EDGE_" + prefix + "_" + str(i).zfill(2) + ".jpg <- " + src_id)
        except Exception as e:
            print("  FAILED " + cat + " #" + str(i) + ": " + str(e))

    for unavail in ["multiple_leaves", "unsupported_crop"]:
        d = TESTING_DIR / "edge_cases" / unavail
        d.mkdir(parents=True, exist_ok=True)
        (d / "NOT_AVAILABLE.txt").write_text(
            unavail + ": not available in existing source data.\n"
            "No external downloads or synthetic images used per project rules.\n"
        )
        print("  NOTE: " + unavail + " -> NOT_AVAILABLE.txt written")

    # ── Manifest
    fields = ["test_id", "crop", "expected_class", "source_dataset",
              "source_path", "original_filename", "purpose"]
    manifest_path = TESTING_DIR / "testing_manifest.csv"
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(manifest_rows)
    print("\nManifest written -> " + str(manifest_path))

    # ── Integrity check
    print("\n[INTEGRITY CHECK]")
    from PIL import Image
    all_imgs = list(TESTING_DIR.rglob("*.jpg")) + list(TESTING_DIR.rglob("*.png"))
    bad = []
    for p in all_imgs:
        try:
            with Image.open(p) as img:
                img.verify()
        except Exception as e:
            bad.append((str(p), str(e)))
    if bad:
        print("UNREADABLE files:")
        for b in bad:
            print("  " + str(b))
    else:
        print("All " + str(len(all_imgs)) + " images are valid and readable.")

    # ── Final report
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print("Total images copied    : " + str(total))
    print("Turmeric images        : " + str(tur))
    print("Citrus images          : " + str(cit))
    print("Edge case images       : " + str(edge))
    print("Skipped classes        : " + (", ".join(skipped) if skipped else "None"))
    print("TESTING folder         : " + str(TESTING_DIR))
    print("Manifest CSV           : " + str(manifest_path))
    print()
    print("Unavailable edge cases (no source data, no synthetic images):")
    print("  multiple_leaves    : not available in existing source data")
    print("  unsupported_crop   : not available in existing source data")
    print()
    print("Original datasets      : UNTOUCHED (read-only via ZIP reader)")
    print("Model/training files   : UNTOUCHED")
    print("No file was moved or deleted from DATASET/")
    print("=" * 60)


if __name__ == "__main__":
    main()
