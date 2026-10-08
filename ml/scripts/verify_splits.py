#!/usr/bin/env python3
"""
verify_splits.py — Phase 5B: Final Split Source-of-Truth Verification

Checks:
  1. Total row counts
  2. Class counts and expected class membership
  3. No duplicate SHA-256 within each split
  4. No SHA-256 overlap across train/val/test (leakage check)
  5. No duplicate_group_id leakage across train/val/test
  6. No external-test contamination (SHA-256 of external not in train/val/test)
  7. No missing image paths (blank absolute_path)
  8. No missing class labels (blank final_class)
  9. Every referenced image file actually exists on disk
 10. Actual split proportions documented

Output:
  data/reports/phase5_split_final_verification.md
"""

import csv
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SPLITS_DIR = Path("data/metadata/splits")
REPORTS_DIR = Path("data/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

TURMERIC_SPLITS = {
    "train": SPLITS_DIR / "turmeric_train.csv",
    "val":   SPLITS_DIR / "turmeric_val.csv",
    "test":  SPLITS_DIR / "turmeric_test.csv",
}
CITRUS_SPLITS = {
    "train": SPLITS_DIR / "citrus_train.csv",
    "val":   SPLITS_DIR / "citrus_val.csv",
    "test":  SPLITS_DIR / "citrus_test.csv",
}
CITRUS_EXTERNAL = SPLITS_DIR / "citrus_external_test.csv"

EXPECTED_TURMERIC_CLASSES = {"Dry Leaf", "Healthy", "Leaf Blotch", "Leaf Spot"}
EXPECTED_CITRUS_CLASSES = {
    "Algal_Leaf_Spot", "Anthracnose", "Bacterial Blight", "Black Spot",
    "Citrus Canker", "Citrus Hindu Mite", "Citrus Leafminer", "Citrus_Pest",
    "Citrus_Scab", "Curl Leaf", "Dry Leaf", "Greening", "Healthy",
    "Lemon_Sooty_Mold", "Melanose", "Spider Mites",
    "Swallowtail Larval Herbivory (Deficiency)", "Yellow_Spot",
}
EXPECTED_EXTERNAL_CLASSES = {
    "Black Spot", "Citrus Canker", "Greening", "Healthy", "Melanose"
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_splits(crop: str, splits: dict[str, Path], expected_classes: set) -> dict:
    """Run all checks for a crop's train/val/test splits. Returns results dict."""
    results = {"crop": crop, "checks": [], "errors": [], "warnings": [], "counts": {}}
    checks = results["checks"]
    errors = results["errors"]
    warnings = results["warnings"]

    # Load all splits
    data = {}
    for split, path in splits.items():
        if not path.exists():
            errors.append(f"MISSING FILE: {path}")
            return results
        data[split] = load_csv(path)

    # ------------------------------------------------------------------
    # Check 1: Total rows
    # ------------------------------------------------------------------
    totals = {s: len(rows) for s, rows in data.items()}
    total_all = sum(totals.values())
    results["counts"]["per_split"] = totals
    results["counts"]["total"] = total_all
    checks.append(f"✅ CHECK 1 — Total rows: train={totals['train']}, val={totals['val']}, test={totals['test']}, TOTAL={total_all}")

    # ------------------------------------------------------------------
    # Check 2: Class counts + expected classes
    # ------------------------------------------------------------------
    for split, rows in data.items():
        classes = Counter(r["final_class"] for r in rows)
        found = set(classes.keys())
        missing = expected_classes - found
        extra = found - expected_classes
        if missing:
            errors.append(f"CHECK 2 — {split}: MISSING CLASSES: {sorted(missing)}")
        if extra:
            warnings.append(f"CHECK 2 — {split}: UNEXPECTED CLASSES: {sorted(extra)}")
        if not missing and not extra:
            checks.append(f"✅ CHECK 2 — {split}: All {len(expected_classes)} expected classes present")
        results["counts"][f"{split}_classes"] = dict(sorted(classes.items()))

    # ------------------------------------------------------------------
    # Check 3: No duplicate SHA-256 within each split
    # ------------------------------------------------------------------
    for split, rows in data.items():
        sha_counter = Counter(r["sha256"] for r in rows if r.get("sha256","").strip())
        intra_dups = {sha: cnt for sha, cnt in sha_counter.items() if cnt > 1}
        if intra_dups:
            errors.append(f"CHECK 3 — {split}: {len(intra_dups)} duplicate SHA-256 hashes within partition")
        else:
            checks.append(f"✅ CHECK 3 — {split}: No intra-partition SHA-256 duplicates")

    # ------------------------------------------------------------------
    # Check 4: No SHA-256 overlap across train/val/test
    # ------------------------------------------------------------------
    sha_sets = {s: set(r["sha256"] for r in rows if r.get("sha256","").strip())
                for s, rows in data.items()}
    tv = sha_sets["train"] & sha_sets["val"]
    tt = sha_sets["train"] & sha_sets["test"]
    vt = sha_sets["val"] & sha_sets["test"]
    leak = False
    if tv:
        errors.append(f"CHECK 4 — LEAKAGE: {len(tv)} SHA-256 overlap between train and val")
        leak = True
    if tt:
        errors.append(f"CHECK 4 — LEAKAGE: {len(tt)} SHA-256 overlap between train and test")
        leak = True
    if vt:
        errors.append(f"CHECK 4 — LEAKAGE: {len(vt)} SHA-256 overlap between val and test")
        leak = True
    if not leak:
        checks.append("✅ CHECK 4 — Zero SHA-256 cross-partition leakage (train/val/test)")

    # ------------------------------------------------------------------
    # Check 5: No duplicate_group_id leakage across train/val/test
    # ------------------------------------------------------------------
    # A duplicate group should not appear in more than one partition
    group_splits = defaultdict(set)
    for split, rows in data.items():
        for r in rows:
            gid = r.get("duplicate_group_id", "").strip()
            if gid and gid.lower() not in ("", "none", "nan"):
                group_splits[gid].add(split)
    leaked_groups = {gid: parts for gid, parts in group_splits.items() if len(parts) > 1}
    if leaked_groups:
        errors.append(f"CHECK 5 — DUPLICATE GROUP LEAKAGE: {len(leaked_groups)} groups span multiple partitions")
        for gid, parts in list(leaked_groups.items())[:5]:
            errors.append(f"  group '{gid}' appears in: {sorted(parts)}")
    else:
        checks.append("✅ CHECK 5 — No duplicate group ID cross-partition leakage")

    # ------------------------------------------------------------------
    # Check 7 & 8: No missing paths or labels
    # ------------------------------------------------------------------
    for split, rows in data.items():
        blank_path  = [r for r in rows if not r.get("absolute_path","").strip()]
        blank_label = [r for r in rows if not r.get("final_class","").strip()]
        if blank_path:
            errors.append(f"CHECK 7 — {split}: {len(blank_path)} rows with blank absolute_path")
        if blank_label:
            errors.append(f"CHECK 8 — {split}: {len(blank_label)} rows with blank final_class")
        if not blank_path and not blank_label:
            checks.append(f"✅ CHECK 7+8 — {split}: No missing paths or labels")

    # ------------------------------------------------------------------
    # Check 9: Every referenced image exists on disk
    # ------------------------------------------------------------------
    for split, rows in data.items():
        missing_files = []
        for r in rows:
            p = r.get("absolute_path","").strip()
            if p and not Path(p).exists():
                missing_files.append(p)
        if missing_files:
            errors.append(f"CHECK 9 — {split}: {len(missing_files)} image files NOT found on disk")
            for mf in missing_files[:3]:
                errors.append(f"  Example: {mf}")
        else:
            checks.append(f"✅ CHECK 9 — {split}: All {len(rows)} image files verified on disk")

    return results


def check_external(external_path: Path, citrus_splits: dict[str, Path]) -> dict:
    """Check external test set is not contaminated in citrus train/val/test."""
    results = {"checks": [], "errors": [], "warnings": [], "counts": {}}
    checks, errors = results["checks"], results["errors"]

    if not external_path.exists():
        errors.append(f"MISSING: {external_path}")
        return results

    ext_rows = load_csv(external_path)
    results["counts"]["external_total"] = len(ext_rows)
    ext_classes = Counter(r["final_class"] for r in ext_rows)
    results["counts"]["external_classes"] = dict(sorted(ext_classes.items()))
    checks.append(f"✅ CHECK EXT-1 — External test: {len(ext_rows)} rows, {len(ext_classes)} classes")

    # Check no missing paths/labels
    blank_path  = sum(1 for r in ext_rows if not r.get("absolute_path","").strip())
    blank_label = sum(1 for r in ext_rows if not r.get("final_class","").strip())
    if blank_path or blank_label:
        errors.append(f"CHECK EXT-2 — External: {blank_path} blank paths, {blank_label} blank labels")
    else:
        checks.append("✅ CHECK EXT-2 — External: No blank paths or labels")

    # Check images exist
    missing_files = [r["absolute_path"] for r in ext_rows if not Path(r["absolute_path"]).exists()]
    if missing_files:
        errors.append(f"CHECK EXT-3 — External: {len(missing_files)} missing image files")
    else:
        checks.append(f"✅ CHECK EXT-3 — External: All {len(ext_rows)} files verified on disk")

    # Check 6: No SHA-256 contamination in citrus train/val/test
    ext_sha = set(r["sha256"] for r in ext_rows if r.get("sha256","").strip())
    for split, path in citrus_splits.items():
        if not path.exists():
            continue
        split_rows = load_csv(path)
        split_sha = set(r["sha256"] for r in split_rows if r.get("sha256","").strip())
        overlap = ext_sha & split_sha
        if overlap:
            errors.append(f"CHECK 6 — CONTAMINATION: {len(overlap)} external images appear in citrus_{split}")
        else:
            checks.append(f"✅ CHECK 6 — No external image contamination in citrus_{split}")

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("LeafLens Phase 5B — Final Split Verification")
    print("=" * 60)

    turmeric_results = check_splits("TURMERIC", TURMERIC_SPLITS, EXPECTED_TURMERIC_CLASSES)
    citrus_results   = check_splits("CITRUS",   CITRUS_SPLITS,   EXPECTED_CITRUS_CLASSES)
    external_results = check_external(CITRUS_EXTERNAL, CITRUS_SPLITS)

    all_errors = (turmeric_results["errors"] + citrus_results["errors"] + external_results["errors"])
    all_warnings = (turmeric_results["warnings"] + citrus_results["warnings"] + external_results["warnings"])

    # ------------------------------------------------------------------
    # Compute proportions
    # ------------------------------------------------------------------
    def proportions(counts):
        total = counts["total"]
        ps = counts["per_split"]
        return {s: (n, f"{100*n/total:.1f}%") for s, n in ps.items()}

    t_props = proportions(turmeric_results["counts"])
    c_props = proportions(citrus_results["counts"])

    # ------------------------------------------------------------------
    # Print to console
    # ------------------------------------------------------------------
    for result in [turmeric_results, citrus_results]:
        print(f"\n{'='*40}")
        print(f"  {result['crop']}")
        print(f"{'='*40}")
        for c in result["checks"]:
            print(f"  {c}")
        for w in result["warnings"]:
            print(f"  ⚠️  {w}")
        for e in result["errors"]:
            print(f"  ❌ {e}")

    print(f"\n{'='*40}")
    print("  EXTERNAL TEST (CITRUS)")
    print(f"{'='*40}")
    for c in external_results["checks"]:
        print(f"  {c}")
    for e in external_results["errors"]:
        print(f"  ❌ {e}")

    # ------------------------------------------------------------------
    # Write markdown report
    # ------------------------------------------------------------------
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    overall = "✅ PASS — ALL CHECKS PASSED" if not all_errors else f"❌ FAIL — {len(all_errors)} ERROR(S) FOUND"

    md_lines = [
        "# Phase 5B — Final Split Source-of-Truth Verification",
        f"> **Generated**: {ts}",
        f"> **Overall Result**: {overall}",
        "",
        "---",
        "",
        "## Summary Table",
        "",
        "| Crop | Split | Count | % of Total |",
        "|------|-------|------:|------------|",
    ]
    tc = turmeric_results["counts"]
    cc = citrus_results["counts"]
    for s in ["train", "val", "test"]:
        n, pct = t_props[s]
        md_lines.append(f"| Turmeric | {s} | {n} | {pct} |")
    md_lines.append(f"| Turmeric | **TOTAL** | **{tc['total']}** | 100% |")
    for s in ["train", "val", "test"]:
        n, pct = c_props[s]
        md_lines.append(f"| Citrus | {s} | {n} | {pct} |")
    md_lines.append(f"| Citrus | **TOTAL** | **{cc['total']}** | 100% |")
    md_lines.append(f"| Citrus | external_test | {external_results['counts'].get('external_total', 'N/A')} | quarantined |")

    # Turmeric class table
    md_lines += [
        "",
        "---",
        "",
        "## Turmeric — Per-Class Counts",
        "",
        "| Class | Train | Val | Test | Total |",
        "|-------|------:|----:|-----:|------:|",
    ]
    t_all_classes = sorted(EXPECTED_TURMERIC_CLASSES)
    for cls in t_all_classes:
        tr = tc.get("train_classes", {}).get(cls, 0)
        vl = tc.get("val_classes", {}).get(cls, 0)
        te = tc.get("test_classes", {}).get(cls, 0)
        md_lines.append(f"| {cls} | {tr} | {vl} | {te} | {tr+vl+te} |")

    # Citrus class table
    md_lines += [
        "",
        "---",
        "",
        "## Citrus — Per-Class Counts",
        "",
        "| Class | Train | Val | Test | Total |",
        "|-------|------:|----:|-----:|------:|",
    ]
    c_all_classes = sorted(EXPECTED_CITRUS_CLASSES)
    for cls in c_all_classes:
        tr = cc.get("train_classes", {}).get(cls, 0)
        vl = cc.get("val_classes", {}).get(cls, 0)
        te = cc.get("test_classes", {}).get(cls, 0)
        md_lines.append(f"| {cls} | {tr} | {vl} | {te} | {tr+vl+te} |")

    # External test class table
    md_lines += [
        "",
        "---",
        "",
        "## Citrus External Test — Per-Class Counts",
        "",
        "| Class | Count |",
        "|-------|------:|",
    ]
    for cls, cnt in sorted(external_results["counts"].get("external_classes", {}).items()):
        md_lines.append(f"| {cls} | {cnt} |")

    # Checks
    md_lines += ["", "---", "", "## Check Results", ""]
    for crop_name, res in [("Turmeric", turmeric_results), ("Citrus", citrus_results)]:
        md_lines.append(f"### {crop_name}")
        for c in res["checks"]:
            md_lines.append(f"- {c}")
        for w in res["warnings"]:
            md_lines.append(f"- ⚠️  {w}")
        for e in res["errors"]:
            md_lines.append(f"- ❌ {e}")
        md_lines.append("")

    md_lines.append("### External Test")
    for c in external_results["checks"]:
        md_lines.append(f"- {c}")
    for e in external_results["errors"]:
        md_lines.append(f"- ❌ {e}")

    # Verdict
    md_lines += [
        "",
        "---",
        "",
        "## Verdict",
        "",
        f"**{overall}**",
        "",
    ]
    if all_errors:
        md_lines.append("### Errors — STOP. Do not proceed to training.")
        for e in all_errors:
            md_lines.append(f"- {e}")
    if all_warnings:
        md_lines.append("")
        md_lines.append("### Warnings")
        for w in all_warnings:
            md_lines.append(f"- {w}")
    if not all_errors:
        md_lines += [
            "All split integrity checks passed. The Phase 4 split CSV files are confirmed as the",
            "source of truth for Phase 5B model training.",
            "",
            "Splits are **LOCKED** — do NOT regenerate.",
        ]

    report_path = REPORTS_DIR / "phase5_split_final_verification.md"
    report_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"\n✅ Report written → {report_path}")

    if all_errors:
        print(f"\n❌ STOP: {len(all_errors)} error(s) found. Fix before training.")
        sys.exit(1)
    else:
        print("\n✅ ALL CHECKS PASSED. Safe to proceed to training.")
        sys.exit(0)


if __name__ == "__main__":
    main()
