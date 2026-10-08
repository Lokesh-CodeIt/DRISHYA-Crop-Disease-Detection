# DRISHYA — Dataset Documentation

## Overview

DRISHYA uses curated subsets of publicly available plant disease image datasets. This document describes the sources, curation process, class mapping, split strategy, and data governance policy.

---

## Source Datasets

### Turmeric

| Dataset | Classes Used | Notes |
|---|---|---|
| Image Dataset for Turmeric Plant Leaf Disease Detection | Healthy, Leaf Blotch | Kaggle source |
| Turmeric Plant Disease Dataset Advancing AI for Agricultural Sustainability | Dry Leaf, Leaf Blotch, Leaf Spot, Healthy | Includes augmented and original subsets |
| Turmeric Plant Disease (1) | Supplementary | Additional class balance support |

**Final Turmeric classes:** Healthy, Dry Leaf, Leaf Blotch, Leaf Spot (4 classes)

### Citrus

| Dataset | Classes Used | Notes |
|---|---|---|
| Large-Scale Lemon Leaf Disease and Pest Image Data | Multiple disease and pest classes | Kaggle source |
| A Citrus Fruits and Leaves Dataset for Detection and Classification of Citrus Diseases through Machine Learning | Multiple citrus disease classes | Kaggle source |

**Final Citrus classes:** 18 classes (Algal Leaf Spot, Anthracnose, Bacterial Blight, Black Spot, Citrus Canker, Citrus Hindu Mite, Citrus Leafminer, Citrus Pest, Citrus Scab, Curl Leaf, Dry Leaf, Greening, Healthy, Lemon Sooty Mold, Melanose, Spider Mites, Swallowtail Larval Herbivory (Deficiency), Yellow Spot)

---

## Curation Process

1. **Integrity Inspection** (`ml/scripts/inspect_datasets.py`) — Non-destructive read-only audit of raw ZIPs
2. **RGB Standardization** (`ml/scripts/clean_datasets.py`) — Convert to RGB, validate dimensions, generate SHA-256 provenance hashes
3. **Duplicate Detection** (`ml/scripts/detect_duplicates.py`) — SHA-256 exact-match + perceptual dHash near-duplicate detection
4. **Master Manifests** — `data/metadata/turmeric_master_manifest.csv` and `data/metadata/citrus_master_manifest.csv` track every image with integrity status, duplicate group, and model-candidacy flag
5. **Phase 3 Curation Report** — `data/reports/phase3_curation_report.md`

All curation operations are **non-destructive**: original files are never moved or modified.

---

## Train / Validation / Test Splits

Stratified 70 / 15 / 15 splits were generated using fixed random seeds for reproducibility.

| Split file | Purpose |
|---|---|
| `data/metadata/splits/turmeric_train.csv` | Turmeric training set |
| `data/metadata/splits/turmeric_val.csv` | Turmeric validation set |
| `data/metadata/splits/turmeric_test.csv` | Turmeric internal test set |
| `data/metadata/splits/citrus_train.csv` | Citrus training set |
| `data/metadata/splits/citrus_val.csv` | Citrus validation set |
| `data/metadata/splits/citrus_test.csv` | Citrus internal test set |
| `data/metadata/splits/citrus_external_test.csv` | Citrus external (cross-dataset) test set |

Model manifests (`turmeric_model_manifest.csv`, `citrus_model_manifest.csv`) include only images with `is_candidate_for_model = True` and `duplicate_status = unique`.

---

## Citrus External Test Set

A separate, geographically distinct citrus image subset not seen during training or validation was reserved as an external test set. This is used for cross-dataset generalization evaluation only.

External test performance: Accuracy 66.01% | Macro F1 0.4892 (vs internal 92.73% / 0.8863)

This demonstrates domain shift between laboratory-sourced training images and external field images.

---

## Dataset Limitations

- All source datasets originate from publicly available Kaggle repositories; geographic diversity is limited
- Turmeric dataset sources overlap in some classes — deduplication was applied
- No field-collected images from Indian agricultural contexts were included in this version
- Multi-source class merging (e.g., combining Turmeric datasets) introduces label heterogeneity risks mitigated by careful class mapping (see `data/reports/turmeric_class_mapping.md`)

---

## Data Governance

- **No raw datasets are committed to this repository**
- Raw dataset ZIPs are excluded by `.gitignore`
- Dataset manifests (CSV) are committed as provenance records
- SHA-256 hashes in manifests allow future integrity verification
- Datasets are sourced from public Kaggle repositories; their original licenses apply
- No dataset redistribution through this repository

---

## Contact Sheet Reports

Visual contact sheet images were generated during Phase 2 inspection and are stored in `data/reports/contact_sheets/`. Two large contact sheets (>7 MB each) are included for reference.

---

## Reproducing Splits

To regenerate splits from raw datasets (requires local dataset ZIPs in `DATASET/`):

```bash
python ml/scripts/inspect_datasets.py
python ml/scripts/clean_datasets.py
python ml/scripts/detect_duplicates.py
python ml/scripts/run_phase3_curation.py
python ml/scripts/run_phase4_split.py
python ml/scripts/verify_splits.py
```
