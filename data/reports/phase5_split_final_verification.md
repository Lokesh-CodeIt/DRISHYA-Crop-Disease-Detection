# Phase 5B — Final Split Source-of-Truth Verification
> **Generated**: 2026-09-30T18:08:00Z
> **Overall Result**: ✅ PASS — ALL INTEGRITY CHECKS PASSED

---

## Summary Table

| Crop | Split | Count | % of Total |
|------|-------|------:|------------|
| Turmeric | train | 870 | 70.0% |
| Turmeric | val | 187 | 15.0% |
| Turmeric | test | 186 | 15.0% |
| Turmeric | **TOTAL** | **1,243** | 100% |
| Citrus | train | 10,435 | 70.0% |
| Citrus | val | 2,235 | 15.0% |
| Citrus | test | 2,241 | 15.0% |
| Citrus | **TOTAL** | **14,911** | 100% |
| Citrus | external_test | 609 | quarantined |

> [!NOTE]
> Minor integer rounding (±1–2 images) exists at per-class level due to stratified splitting. The current CSV files are the authoritative source of truth.

---

## Turmeric — Per-Class Counts

| Class | Train | Val | Test | Total |
|-------|------:|----:|-----:|------:|
| Dry Leaf | 142 | 30 | 31 | 203 |
| Healthy | 287 | 62 | 61 | 410 |
| Leaf Blotch | 306 | 66 | 65 | 437 |
| Leaf Spot | 135 | 29 | 29 | 193 |
| **TOTAL** | **870** | **187** | **186** | **1,243** |

### Turmeric Class Weights (balanced inverse-frequency, train set only)

| Class | Train Count | Weight |
|-------|------------:|-------:|
| Dry Leaf | 142 | 1.5317 |
| Healthy | 287 | 0.7578 |
| Leaf Blotch | 306 | 0.7108 |
| Leaf Spot | 135 | 1.6111 |

---

## Citrus — Per-Class Counts

| Class | Train | Val | Test | Total |
|-------|------:|----:|-----:|------:|
| Algal_Leaf_Spot | 587 | 126 | 126 | 839 |
| Anthracnose | 591 | 127 | 126 | 844 |
| Bacterial Blight | 85 | 18 | 19 | 122 |
| Black Spot | 486 | 104 | 105 | 695 |
| Citrus Canker | 1,046 | 224 | 225 | 1,495 |
| Citrus Hindu Mite | 381 | 82 | 81 | 544 |
| Citrus Leafminer | 542 | 116 | 117 | 775 |
| Citrus_Pest | 379 | 81 | 82 | 542 |
| Citrus_Scab | 233 | 50 | 50 | 333 |
| Curl Leaf | 1,093 | 234 | 235 | 1,562 |
| Dry Leaf | 136 | 29 | 30 | 195 |
| Greening | 1,220 | 261 | 262 | 1,743 |
| Healthy | 1,147 | 246 | 245 | 1,638 |
| Lemon_Sooty_Mold | 1,114 | 239 | 239 | 1,592 |
| Melanose | 132 | 28 | 28 | 188 |
| Spider Mites | 88 | 19 | 18 | 125 |
| Swallowtail Larval Herbivory (Deficiency) | 706 | 151 | 152 | 1,009 |
| Yellow_Spot | 469 | 100 | 101 | 670 |
| **TOTAL** | **10,435** | **2,235** | **2,241** | **14,911** |

---

## Citrus External Test — Per-Class Counts

| Class | Count |
|-------|------:|
| Black Spot | 171 |
| Citrus Canker | 163 |
| Greening | 204 |
| Healthy | 58 |
| Melanose | 13 |
| **TOTAL** | **609** |

---

## Check Results

### Check 1 — Total Row Counts ✅
All 7 CSV files match expected row counts exactly.

### Check 2 — Expected Classes Present ✅
- Turmeric: All 4 classes in train/val/test
- Citrus: All 18 classes in train/val/test
- External: 5 cross-dataset classes confirmed

### Check 3 — No Intra-Partition SHA-256 Duplicates ✅
Zero duplicate SHA-256 hashes within any single partition.

### Check 4 — No Cross-Partition SHA-256 Leakage ✅
- Turmeric: Zero overlap between train/val/test
- Citrus: Zero overlap between train/val/test

### Check 5 — No Duplicate-Group Leakage ✅
No `duplicate_group_id` spans multiple partitions in either crop.

### Check 6 — No External Test Contamination ✅
Zero external test SHA-256 hashes appear in citrus train, val, or test.

### Check 7 — No Missing Absolute Paths ✅
Zero blank `absolute_path` fields across all 7 files.

### Check 8 — No Missing Class Labels ✅
Zero blank `final_class` fields across all 7 files.

### Check 9 — Image Access Verified ✅ (ZIP-native by design)

> [!IMPORTANT]
> All `absolute_path` values use **virtual ZIP path notation** (`archive.zip#inner/path.jpg`).
> Images are stored inside the original DATASET ZIP archives — never extracted to disk.
> The ZIP-aware DataLoader (`open_pil_image()`) reads them directly without touching DATASET/.
> All three path formats were verified by reading actual image bytes:

| Format | Depth | Bytes Read | Status |
|--------|-------|------------|--------|
| Single ZIP: `LargeScaleLemon.zip#class/img.jpg` | 1 | 204,340 | ✅ |
| Double ZIP: `AdvancingAI.zip#Inner.zip#class/img.jpg` | 2 | 184,780 | ✅ |
| Prefixed double ZIP: `CitrusDS.zip#prefix/Inner.zip#class/img.jpg` | 2 | 472,447 | ✅ |

### Check 10 — Split Proportions Documented ✅

| Crop | Train | Val | Test |
|------|-------|-----|------|
| Turmeric | 70.0% (870) | 15.0% (187) | 15.0% (186) |
| Citrus | 70.0% (10,435) | 15.0% (2,235) | 15.0% (2,241) |

---

## Verdict

**✅ ALL 10 CHECKS PASSED. SPLITS ARE LOCKED.**

All split CSV files are confirmed as the source of truth for Phase 5B training.
No leakage, no contamination, no structural errors found.
**Splits must NOT be regenerated.**

| File | Rows | Status |
|------|-----:|--------|
| turmeric_train.csv | 870 | ✅ Locked |
| turmeric_val.csv | 187 | ✅ Locked |
| turmeric_test.csv | 186 | ✅ Locked |
| citrus_train.csv | 10,435 | ✅ Locked |
| citrus_val.csv | 2,235 | ✅ Locked |
| citrus_test.csv | 2,241 | ✅ Locked |
| citrus_external_test.csv | 609 | ✅ Quarantined |
