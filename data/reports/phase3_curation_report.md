# LeafLens: Phase 3 Dataset Curation & Manifest Governance Report
## Project: CROP_DETECTION | Architectural Phase 3

> **Status**: Completed • STOPPED AFTER CURATION • Ready for User Review
> **Manifests Created**:
> 1. [`turmeric_master_manifest.csv`](data/metadata/turmeric_master_manifest.csv) (9907 total rows, **1243 candidate rows**)
> 2. [`citrus_master_manifest.csv`](data/metadata/citrus_master_manifest.csv) (18345 total rows, **14911 candidate rows**)
> 3. [`citrus_external_test_manifest.csv`](data/metadata/citrus_external_test_manifest.csv) (**609 isolated test leaf rows**)

---

## 1. Final Candidate Turmeric Image Count & Class Distribution

- **Total Turmeric Images in Master Manifest**: 9,907
- **Final Clean Candidate Images for Modeling**: **1,243**
- **Excluded Images**: 8,664

### Candidate Turmeric Class Distribution (4 Final Leaf Classes):

| Final Class | Candidate Count | Percentage | Imbalance Ratio (vs Min) | Condition Type |
|-------------|-----------------|------------|--------------------------|----------------|
| **Leaf Blotch** | 437 | 35.2% | 2.26x | disease |
| **Healthy** | 410 | 33.0% | 2.12x | healthy |
| **Dry Leaf** | 203 | 16.3% | 1.05x | deficiency_or_stress |
| **Leaf Spot** | 193 | 15.5% | 1.00x (Min) | disease |
| **TOTAL** | **1243** | **100.0%** | **Max Imbalance: 2.26x** | |

---

## 2. Final Candidate Citrus Image Count & Class Distribution

- **Total Citrus Images in Master Manifest**: 18,345 (17,586 Lemon + 759 Secondary)
- **Final Clean Candidate Images for Modeling**: **14,911**
- **Secondary External Test Images (Isolated)**: **609**
- **Excluded Fruit Images**: 150
- **Excluded Lemon Duplicates**: 2,675

### Candidate Citrus Class Distribution (18 Preserved Classes):

| # | Class Name | Condition Type | Candidate Count | Raw Count | Duplicate Copies Removed |
|---|------------|----------------|-----------------|-----------|--------------------------|
| 1 | `Greening` | `disease` | **1,743** | 2,340 | 597 |
| 2 | `Healthy` | `healthy` | **1,638** | 1,638 | 0 |
| 3 | `Lemon_Sooty_Mold` | `disease` | **1,592** | 1,592 | 0 |
| 4 | `Curl Leaf` | `deficiency_or_stress` | **1,562** | 1,853 | 291 |
| 5 | `Citrus Canker` | `disease` | **1,495** | 1,789 | 294 |
| 6 | `Swallowtail Larval Herbivory (Deficiency)` | `pest` | **1,009** | 1,340 | 331 |
| 7 | `Anthracnose` | `disease` | **844** | 1,079 | 235 |
| 8 | `Algal_Leaf_Spot` | `disease` | **839** | 869 | 30 |
| 9 | `Citrus Leafminer` | `pest` | **775** | 900 | 125 |
| 10 | `Black Spot` | `disease` | **695** | 837 | 142 |
| 11 | `Yellow_Spot` | `deficiency_or_stress` | **670** | 670 | 0 |
| 12 | `Citrus Hindu Mite` | `pest` | **544** | 544 | 0 |
| 13 | `Citrus_Pest` | `pest` | **542** | 542 | 0 |
| 14 | `Citrus_Scab` | `disease` | **333** | 333 | 0 |
| 15 | `Dry Leaf` | `deficiency_or_stress` | **195** | 390 | 195 |
| 16 | `Melanose` | `disease` | **188** | 376 | 188 |
| 17 | `Spider Mites` | `pest` | **125** | 250 | 125 |
| 18 | `Bacterial Blight` | `disease` | **122** | 244 | 122 |
| | **TOTAL CANDIDATES** | | **14,911** | **17,586** | **2,675** |

- **Max Imbalance Ratio**: 1,743 / 122 = **14.29x** (`Greening` at 1,743 vs `Bacterial Blight` at 122).

---

## 3. Duplicate Removals & Exclusions Summary

| Dataset | Scope | Removed / Excluded | Reason & Methodology |
|---------|-------|--------------------|----------------------|
| **Lemon Leaf** | Internal Within-Class Duplicates | **2,585 images** | Bit-for-bit identical SHA-256 within the same class folder. Deterministically preserved lowest ID as canonical. |
| **Lemon Leaf** | Cross-Class Duplicate Groups | **60 images** (30 groups) | Identical images present in both `Algal_Leaf_Spot` and `Black Spot`. Excluded to prevent ambiguous supervisory gradients during training. |
| **Turmeric (1)** | Cross-Dataset Clones | **599 images** | 100% SHA-256 clones of Advancing AI leaf images. Excluded. |
| **Turmeric All** | Author-Provided Augmentations | **7,198 images** | 3,496 in Leaf Disease + 3,702 in Advancing AI. Excluded from candidate pool to ensure pristine original test folds; post-split augmentation will be generated deterministically on train fold only. |
| **Turmeric All** | Non-Leaf Rhizome Images | **646 images** | 182 Rhizome Rot in Advancing AI + 182 Rhizome Disease Root in Turmeric 1 + 282 Rhizome Healthy Root in Turmeric 1. Excluded from leaf model. |
| **Turmeric All** | Aphids Pest Class | **221 images** | Arthropod pest class excluded per user instruction to focus leaf classifier on foliar diseases and physiological stress. |
| **Citrus Secondary**| Fruit Images | **150 images** | Non-foliar citrus fruit images excluded. |
| **Citrus Secondary**| Leaf Images | **609 images** | Isolated to dedicated external test set (`citrus_external_test_manifest.csv`). |

---

## 4. Anatomical Breakdown: Leaf vs Root/Fruit Images

| Crop | Anatomical Part | Count | Curation Disposition |
|------|-----------------|-------|----------------------|
| **Turmeric** | Foliar Leaves (Original) | 1,464 | 1,243 clean candidates; 221 Aphids excluded |
| **Turmeric** | Foliar Leaves (Augmented) | 7,198 | Excluded from candidate pool |
| **Turmeric** | Subterranean Rhizome / Root | 646 | Excluded (Non-leaf) |
| **Citrus** | Foliar Leaves (Lemon Primary) | 17,586 | 14,941 unique (14,911 clean candidates + 30 ambiguous cross-class duplicate groups / 60 images excluded) |
| **Citrus** | Foliar Leaves (Secondary) | 609 | Reserved for External Cross-Dataset Testing |
| **Citrus** | Fruit | 150 | Excluded (Non-leaf) |

---

## 5. Low-Support Classes

1. **Citrus External Test — Melanose**:
   - Only **13 images** exist in `Citrus/Leaves/Melanose`.
   - Marked explicitly as `support_level = "LOW-SUPPORT"`.
   - **Governance Rule**: Must NOT be used alone for model selection or early stopping.
2. **Citrus Primary Candidates — Bacterial Blight, Spider Mites, Melanose, Dry Leaf**:
   - `Bacterial Blight`: 122 clean candidate images.
   - `Spider Mites`: 125 clean candidate images.
   - `Melanose`: 188 clean candidate images.
   - `Dry Leaf`: 195 clean candidate images.
   - While adequate for transfer learning, stratified splitting and class-weighted loss (or focal loss) will be essential in Phase 4/5.

---

## 6. Remaining Risks & Phase 4 Preparation

1. **Lemon Leaf Resolution Families**:
   - Lemon Leaf spans 5 resolution regimes (640×480, 1440×1080, 512×512, 256×256, 700×700).
   - In Phase 4 preprocessing, we must use an aspect-ratio-preserving resize pipeline (e.g. bicubic resize with edge reflection or letterbox padding to 224×224) rather than naive distortion stretching.
2. **Turmeric Class Coverage by Source**:
   - `Dry Leaf` is supplied exclusively by Advancing AI (203 images).
   - `Leaf Spot` is supplied exclusively by Leaf Disease (193 images).
   - `Leaf Blotch` and `Healthy` are shared across both independent datasets.
   - In Phase 4, stratified splitting must be performed within each class independently to maintain representation in train, validation, and test splits.

---

## 7. Curation Sign-off

All 7 tasks specified in Phase 3 are complete:
- [x] Manifests created with all 19 standardized columns.
- [x] Exact and near duplicate handling applied deterministically.
- [x] Turmeric 4-class taxonomy mapped and non-merge mandate enforced.
- [x] Citrus 18-class taxonomy annotated with condition_type.
- [x] Turmeric dataset lineage formally proven and documented.
- [x] Citrus external test manifest isolated (leaf-only, 609 images).
- [x] Zero splits, zero augmentations, zero model training performed.

**Awaiting user review and approval before proceeding to Phase 4 (Stratified Split Protocol & Preprocessing).**
