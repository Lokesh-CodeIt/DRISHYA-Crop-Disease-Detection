# LeafLens: Dataset Split Quality & Leakage Audit Report
## Phase 4 Final Split Protocol Verification

> **Verification Timestamp**: 2026-09-30
> **Primary Split Seed**: 42 (Secondary evaluation seeds locked: 123, 7)
> **Split Ratios**: 70.0% Train / 15.0% Validation / 15.0% Test (Stratified)
> **Leakage Status**: **ZERO LEAKAGE DETECTED (PASSED)**

---

## 1. Summary Partition Sizes

| Crop | Total Candidate Images | Train Count (70%) | Validation Count (15%) | Test Count (15%) |
|------|------------------------|-------------------|------------------------|------------------|
| **Turmeric** | **1,243** | 870 (70.0%) | 187 (15.0%) | 186 (15.0%) |
| **Citrus (Lemon)** | **14,911** | 10,435 (70.0%) | 2,235 (15.0%) | 2,241 (15.0%) |
| **Citrus External Test** | **609** | *0 (Held Out)* | *0 (Held Out)* | **609 (External)** |

---

## 2. Turmeric Class Distribution Per Split

| Class Name | Total Candidates | Train Count (%) | Val Count (%) | Test Count (%) | Imbalance Ratio (Split) |
|------------|------------------|-----------------|---------------|----------------|-------------------------|
| `Leaf Blotch` | 437 | 306 (35.2%) | 66 (35.3%) | 65 (34.9%) | 2.27x |
| `Healthy` | 410 | 287 (33.0%) | 62 (33.2%) | 61 (32.8%) | 2.13x |
| `Dry Leaf` | 203 | 142 (16.3%) | 30 (16.0%) | 31 (16.7%) | 1.05x |
| `Leaf Spot` | 193 | 135 (15.5%) | 29 (15.5%) | 29 (15.6%) | 1.00x |
| **TOTAL** | **1,243** | **870** | **187** | **186** | **Max: 2.27x** |

---

## 3. Citrus Class Distribution Per Split (All 18 Classes)

| # | Class Name | Total Candidates | Train (70%) | Val (15%) | Test (15%) | Min/Max Range |
|---|------------|------------------|-------------|-----------|------------|---------------|
| 1 | `Greening` | **1,743** | 1,220 | 261 | 262 | 262/1743 (15.0%) |
| 2 | `Healthy` | **1,638** | 1,147 | 246 | 245 | 245/1638 (15.0%) |
| 3 | `Lemon_Sooty_Mold` | **1,592** | 1,114 | 239 | 239 | 239/1592 (15.0%) |
| 4 | `Curl Leaf` | **1,562** | 1,093 | 234 | 235 | 235/1562 (15.0%) |
| 5 | `Citrus Canker` | **1,495** | 1,046 | 224 | 225 | 225/1495 (15.1%) |
| 6 | `Swallowtail Larval Herbivory (Deficiency)` | **1,009** | 706 | 151 | 152 | 152/1009 (15.1%) |
| 7 | `Anthracnose` | **844** | 591 | 127 | 126 | 126/844 (14.9%) |
| 8 | `Algal_Leaf_Spot` | **839** | 587 | 126 | 126 | 126/839 (15.0%) |
| 9 | `Citrus Leafminer` | **775** | 542 | 116 | 117 | 117/775 (15.1%) |
| 10 | `Black Spot` | **695** | 486 | 104 | 105 | 105/695 (15.1%) |
| 11 | `Yellow_Spot` | **670** | 469 | 100 | 101 | 101/670 (15.1%) |
| 12 | `Citrus Hindu Mite` | **544** | 381 | 82 | 81 | 81/544 (14.9%) |
| 13 | `Citrus_Pest` | **542** | 379 | 81 | 82 | 82/542 (15.1%) |
| 14 | `Citrus_Scab` | **333** | 233 | 50 | 50 | 50/333 (15.0%) |
| 15 | `Dry Leaf` | **195** | 136 | 29 | 30 | 30/195 (15.4%) |
| 16 | `Melanose` | **188** | 132 | 28 | 28 | 28/188 (14.9%) |
| 17 | `Spider Mites` | **125** | 88 | 19 | 18 | 18/125 (14.4%) |
| 18 | `Bacterial Blight` | **122** | 85 | 18 | 19 | 19/122 (15.6%) |

---

## 4. Formal Leakage Verification Audit

| Audit Check | Scope | Overlap Detected | Status |
|-------------|-------|------------------|--------|
| **Turmeric SHA-256 Hash Intersection** | Train ∩ Val | **0** | PASSED ✅ |
| **Turmeric SHA-256 Hash Intersection** | Train ∩ Test | **0** | PASSED ✅ |
| **Turmeric SHA-256 Hash Intersection** | Val ∩ Test | **0** | PASSED ✅ |
| **Turmeric Duplicate Group Integrity** | Across All Splits | **0 Cross-Split Groups** | PASSED ✅ |
| **Citrus SHA-256 Hash Intersection** | Train ∩ Val | **0** | PASSED ✅ |
| **Citrus SHA-256 Hash Intersection** | Train ∩ Test | **0** | PASSED ✅ |
| **Citrus SHA-256 Hash Intersection** | Val ∩ Test | **0** | PASSED ✅ |
| **Citrus Duplicate Group Integrity** | Across All Splits | **0 Cross-Split Groups** | PASSED ✅ |
| **Citrus External-Test Contamination** | External ∩ Train | **0** | PASSED ✅ |
| **Citrus External-Test Contamination** | External ∩ Val | **0** | PASSED ✅ |
| **Citrus External-Test Contamination** | External ∩ Test | **0** | PASSED ✅ |

> [!NOTE]
> All members of any candidate group are strictly isolated to a single partition. Canonical image IDs are locked deterministically. No data leakage exists anywhere across splits or across datasets.
