"""
smoke_validation_22class.py — DRISHYA Step B.1
Full Explainability Smoke Validation across all 22 normal classes.

Runs without a live HTTP server by calling DiagnosisService directly.
Writes output to:
  docs/explainability_22_class_validation.csv
  docs/explainability_22_class_validation.md

RULES:
- No model/checkpoint/calibration/frontend modifications.
- Use TESTING/ images only.
- A prediction mismatch is NOT a failure — report honestly.
- Do not call attention regions "lesions" or "defects".
"""

import csv
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

# ------------------------------------------------------------------
# Path setup so we can import the backend package
# ------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.app.services.diagnosis_service import DiagnosisService
from backend.app.services.inference_service import inference_service
from backend.app.models.schemas import CropType, Language

# ------------------------------------------------------------------
# The 22 normal classes with their representative test image (first
# available _01 image from TESTING/<crop>/<class>/)
# ------------------------------------------------------------------
TESTING_ROOT = ROOT / "TESTING"

CASES = [
    # (crop_str, expected_class_label, image_rel_path)
    # ---------- TURMERIC (4 classes) ----------
    ("turmeric", "dry_leaf",     "turmeric/dry_leaf/TUR_dry_leaf_01.jpg"),
    ("turmeric", "healthy",      "turmeric/healthy/TUR_healthy_01.jpg"),
    ("turmeric", "leaf_blotch",  "turmeric/leaf_blotch/TUR_leaf_blotch_01.jpg"),
    ("turmeric", "leaf_spot",    "turmeric/leaf_spot/TUR_leaf_spot_01.jpg"),
    # ---------- CITRUS (18 classes) ----------
    ("citrus", "algal_leaf_spot",
     "citrus/algal_leaf_spot/CIT_algal_leaf_spot_01.jpg"),
    ("citrus", "anthracnose",
     "citrus/anthracnose/CIT_anthracnose_01.jpg"),
    ("citrus", "bacterial_blight",
     "citrus/bacterial_blight/CIT_bacterial_blight_01.jpg"),
    ("citrus", "black_spot",
     "citrus/black_spot/CIT_black_spot_01.jpg"),
    ("citrus", "citrus_canker",
     "citrus/citrus_canker/CIT_citrus_canker_01.jpg"),
    ("citrus", "citrus_hindu_mite",
     "citrus/citrus_hindu_mite/CIT_citrus_hindu_mite_01.jpg"),
    ("citrus", "citrus_leafminer",
     "citrus/citrus_leafminer/CIT_citrus_leafminer_01.jpg"),
    ("citrus", "citrus_pest",
     "citrus/citrus_pest/CIT_citrus_pest_01.jpg"),
    ("citrus", "citrus_scab",
     "citrus/citrus_scab/CIT_citrus_scab_01.jpg"),
    ("citrus", "curl_leaf",
     "citrus/curl_leaf/CIT_curl_leaf_01.jpg"),
    ("citrus", "dry_leaf",
     "citrus/dry_leaf/CIT_dry_leaf_01.jpg"),
    ("citrus", "greening",
     "citrus/greening/CIT_greening_01.jpg"),
    ("citrus", "healthy",
     "citrus/healthy/CIT_healthy_01.jpg"),
    ("citrus", "lemon_sooty_mold",
     "citrus/lemon_sooty_mold/CIT_lemon_sooty_mold_01.jpg"),
    ("citrus", "melanose",
     "citrus/melanose/CIT_melanose_01.jpg"),
    ("citrus", "spider_mites",
     "citrus/spider_mites/CIT_spider_mites_01.jpg"),
    ("citrus", "swallowtail_larval_herbivory_deficiency",
     "citrus/swallowtail_larval_herbivory_deficiency/CIT_swallowtail_larval_herbivory_deficiency_01.jpg"),
    ("citrus", "yellow_spot",
     "citrus/yellow_spot/CIT_yellow_spot_01.jpg"),
]

CSV_FIELDS = [
    "crop",
    "expected_class",
    "predicted_class",
    "raw_probability",
    "calibrated_probability",
    "is_rejected",
    "explanation_available",
    "target_class",
    "target_layer",
    "region_count",
    "explanation_processing_time_ms",
    "match",
    "error",
]


def _safe_round(v, n=4):
    try:
        return round(float(v), n)
    except (TypeError, ValueError):
        return None


def run_one(svc, crop_str, expected, img_rel):
    img_path = TESTING_ROOT / img_rel
    row = {
        "crop": crop_str,
        "expected_class": expected,
        "predicted_class": "ERROR",
        "raw_probability": None,
        "calibrated_probability": None,
        "is_rejected": None,
        "explanation_available": None,
        "target_class": None,
        "target_layer": None,
        "region_count": None,
        "explanation_processing_time_ms": None,
        "match": False,
        "error": "",
    }

    if not img_path.exists():
        row["error"] = f"Image not found: {img_path}"
        return row

    try:
        image_bytes = img_path.read_bytes()
        crop_enum = CropType(crop_str)

        resp = svc.diagnose(
            image_bytes=image_bytes,
            crop=crop_enum,
            language=Language.ENGLISH,
            db=None,
        )

        pred = resp.prediction
        row["predicted_class"] = pred.predicted_class
        row["raw_probability"] = _safe_round(pred.confidence)
        row["calibrated_probability"] = _safe_round(pred.calibrated_confidence)
        row["is_rejected"] = pred.is_rejected
        # Normalise both sides: lowercase, spaces/hyphens → underscores, strip parens
        def _norm(s: str) -> str:
            return (s.lower()
                    .replace("(", "").replace(")", "")
                    .replace(" ", "_").replace("-", "_")
                    .strip("_"))
        row["match"] = (_norm(pred.predicted_class) == _norm(expected))

        expl = resp.explanation
        if expl is not None:
            row["explanation_available"] = expl.explanation_available
            row["target_class"] = expl.target_class
            row["target_layer"] = expl.target_layer
            row["region_count"] = len(expl.regions)
            row["explanation_processing_time_ms"] = _safe_round(expl.processing_time_ms, 2)
        else:
            row["explanation_available"] = False
            row["region_count"] = 0

    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()

    return row


def build_md(rows):
    total = len(rows)
    errors = [r for r in rows if r["error"]]
    correct = [r for r in rows if r["match"]]
    expl_ok = [r for r in rows if r["explanation_available"] is True]
    expl_fail = [r for r in rows if r["explanation_available"] is False]
    times = [r["explanation_processing_time_ms"] for r in rows
             if r["explanation_processing_time_ms"] is not None]
    avg_time = round(sum(times) / len(times), 2) if times else "N/A"
    mismatches = [r for r in rows if not r["match"] and not r["error"]]

    lines = [
        "# DRISHYA Explainability 22-Class Smoke Validation",
        "",
        "> Generated by `tests/smoke_validation_22class.py` — Step B.1",
        "> No models, checkpoints, calibration, or frontend were modified.",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total classes tested | {total} |",
        f"| Prediction accuracy | {len(correct)}/{total} ({round(100*len(correct)/total, 1)}%) |",
        f"| Explanation success rate | {len(expl_ok)}/{total} ({round(100*len(expl_ok)/total, 1)}%) |",
        f"| Explanation failures | {len(expl_fail)} |",
        f"| Average explanation time (ms) | {avg_time} |",
        f"| Runtime errors | {len(errors)} |",
        "",
        "> **Note:** Prediction mismatches are not implementation failures.",
        "> A mismatch means the model's top-1 prediction differed from the folder label.",
        "> This is expected on single-image samples and reflects genuine model uncertainty,",
        "> not a bug in the explainability pipeline.",
        "",
        "---",
        "",
        "## Per-Class Results",
        "",
        "| # | Crop | Expected Class | Predicted Class | Raw Prob | Cal. Prob | Rejected | Expl? | Target Layer | Regions | Expl Time (ms) | Match |",
        "|---|------|----------------|-----------------|----------|-----------|----------|-------|--------------|---------|----------------|-------|",
    ]

    for i, r in enumerate(rows, 1):
        match_sym = "YES" if r["match"] else "NO"
        expl_sym = "YES" if r["explanation_available"] else (
            "NO" if r["explanation_available"] is False else "N/A")
        rej_sym = "Yes" if r["is_rejected"] else (
            "No" if r["is_rejected"] is not None else "N/A")
        raw_p = f"{r['raw_probability']:.4f}" if r["raw_probability"] is not None else "N/A"
        cal_p = f"{r['calibrated_probability']:.4f}" if r["calibrated_probability"] is not None else "N/A"
        layer = r["target_layer"] or "N/A"
        regions = str(r["region_count"]) if r["region_count"] is not None else "N/A"
        t = str(r["explanation_processing_time_ms"]) if r["explanation_processing_time_ms"] is not None else "N/A"
        pred = r["predicted_class"]
        lines.append(
            f"| {i} | {r['crop']} | {r['expected_class']} | {pred} "
            f"| {raw_p} | {cal_p} | {rej_sym} | {expl_sym} "
            f"| `{layer}` | {regions} | {t} | {match_sym} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Prediction Mismatches",
        "",
    ]
    if mismatches:
        lines += [
            "| Crop | Expected | Predicted | Raw Prob |",
            "|------|----------|-----------|----------|",
        ]
        for r in mismatches:
            raw_p = f"{r['raw_probability']:.4f}" if r["raw_probability"] is not None else "N/A"
            lines.append(f"| {r['crop']} | {r['expected_class']} | {r['predicted_class']} | {raw_p} |")
    else:
        lines.append("_No mismatches — all predictions matched expected class labels._")

    lines += [
        "",
        "---",
        "",
        "## Explanation Failures",
        "",
    ]
    if expl_fail:
        lines += [
            "| Crop | Expected | Predicted | Error |",
            "|------|----------|-----------|-------|",
        ]
        for r in expl_fail:
            err = r["error"] or "N/A"
            lines.append(f"| {r['crop']} | {r['expected_class']} | {r['predicted_class']} | {err} |")
    else:
        lines.append("_All explanations generated successfully._")

    if errors:
        lines += [
            "",
            "---",
            "",
            "## Runtime Errors",
            "",
            "| Crop | Expected | Error |",
            "|------|----------|-------|",
        ]
        for r in errors:
            lines.append(f"| {r['crop']} | {r['expected_class']} | `{r['error']}` |")

    lines += [
        "",
        "---",
        "",
        "_End of report._",
    ]

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("DRISHYA — Step B.1: 22-Class Explainability Smoke Validation")
    print("=" * 70)
    print()

    missing = []
    for crop_str, expected, img_rel in CASES:
        p = TESTING_ROOT / img_rel
        if not p.exists():
            missing.append(str(p))
    if missing:
        print("WARNING: The following test images were NOT found:")
        for m in missing:
            print(f"  {m}")
        print()

    print("Loading models into memory (this may take ~30 s) ...")
    inference_service.initialize_models()
    print("Models loaded.\n")

    svc = DiagnosisService()
    rows = []

    for idx, (crop_str, expected, img_rel) in enumerate(CASES, 1):
        print(f"[{idx:02d}/{len(CASES)}] {crop_str:8s} | {expected}")
        t0 = time.perf_counter()
        row = run_one(svc, crop_str, expected, img_rel)
        elapsed = round((time.perf_counter() - t0) * 1000, 1)
        rows.append(row)

        match_sym = "MATCH" if row["match"] else "MISMATCH"
        expl_sym = "OK" if row["explanation_available"] else "FAIL"
        pred = row["predicted_class"]
        raw_p = f"{row['raw_probability']:.4f}" if row["raw_probability"] is not None else "?"
        err = f"  WARN: {row['error']}" if row["error"] else ""
        print(
            f"         pred={pred:<45s} raw={raw_p}  "
            f"{match_sym}  expl={expl_sym}  total={elapsed}ms{err}"
        )

    print()
    print("Writing output files ...")

    docs_dir = ROOT / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    csv_path = docs_dir / "explainability_22_class_validation.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  CSV  -> {csv_path}")

    md_path = docs_dir / "explainability_22_class_validation.md"
    md_path.write_text(build_md(rows), encoding="utf-8")
    print(f"  MD   -> {md_path}")

    total = len(rows)
    correct = sum(1 for r in rows if r["match"])
    expl_ok = sum(1 for r in rows if r["explanation_available"] is True)
    times = [r["explanation_processing_time_ms"] for r in rows
             if r["explanation_processing_time_ms"] is not None]
    avg_time = round(sum(times) / len(times), 2) if times else "N/A"

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Total classes tested    : {total}")
    print(f"  Prediction accuracy     : {correct}/{total}  ({round(100*correct/total, 1)}%)")
    print(f"  Explanation success     : {expl_ok}/{total}  ({round(100*expl_ok/total, 1)}%)")
    print(f"  Avg explanation time    : {avg_time} ms")
    mismatches = [r for r in rows if not r["match"] and not r["error"]]
    if mismatches:
        print(f"  Mismatches ({len(mismatches)}):")
        for r in mismatches:
            print(f"    {r['crop']:8s} | expected={r['expected_class']:<50s} predicted={r['predicted_class']}")
    print()
    print("Done.")


if __name__ == "__main__":
    main()
