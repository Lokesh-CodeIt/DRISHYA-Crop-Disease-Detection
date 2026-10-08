# LeafLens: Phase 4 Final Split Protocol & Experiment Lock Report
## Project: CROP_DETECTION | Architectural Phase 4

> **Status**: COMPLETED • EXPERIMENT PROTOCOL LOCKED • READY FOR REVIEW
> **Execution Mode**: STRICTLY NO TRAINING • NO AUGMENTATION • READ-ONLY ON SOURCE DATA
> **Manifests & Split Files Created**:
> 1. [`turmeric_model_manifest.csv`](data/metadata/turmeric_model_manifest.csv) (1,243 images)
> 2. [`citrus_model_manifest.csv`](data/metadata/citrus_model_manifest.csv) (14,911 images)
> 3. [`turmeric_train.csv`](data/metadata/splits/turmeric_train.csv) (870 images, 70.0%)
> 4. [`turmeric_val.csv`](data/metadata/splits/turmeric_val.csv) (187 images, 14.9%)
> 5. [`turmeric_test.csv`](data/metadata/splits/turmeric_test.csv) (186 images, 15.1%)
> 6. [`citrus_train.csv`](data/metadata/splits/citrus_train.csv) (10,435 images, 70.0%)
> 7. [`citrus_val.csv`](data/metadata/splits/citrus_val.csv) (2,235 images, 15.0%)
> 8. [`citrus_test.csv`](data/metadata/splits/citrus_test.csv) (2,241 images, 15.0%)
> 9. [`citrus_external_test.csv`](data/metadata/splits/citrus_external_test.csv) (609 leaf images)
> 10. [`turmeric_external_protocol.csv`](data/metadata/turmeric_external_protocol.csv) (1,243 rows)

---

## 1. Final Turmeric Sample Count & Partition Breakdown

- **Total Candidate Pool**: **1,243 foliar leaf images** across 4 classes:
  - `Healthy`: 410 images
  - `Leaf Blotch`: 437 images
  - `Dry Leaf`: 203 images
  - `Leaf Spot`: 193 images
- **Train Split (70%)**: **870 images**
- **Validation Split (15%)**: **187 images**
- **Test Split (15%)**: **186 images**
- **Excluded**: Aphids (221), Rhizome Rot (182), Turmeric 1 clones (599), Turmeric 1 roots (464), Author augments (7,198).

---

## 2. Final Citrus Sample Count & Partition Breakdown

- **Total Candidate Pool**: **14,911 foliar leaf images** across all 18 preserved classes:
  - 9 Disease classes (9,482 raw → 8,024 clean candidates)
  - 5 Pest classes (3,576 raw → 3,295 clean candidates)
  - 3 Deficiency/Stress classes (2,913 raw → 2,427 clean candidates)
  - 1 Healthy class (1,638 raw → 1,638 clean candidates)
- **Train Split (70%)**: **10,435 images**
- **Validation Split (15%)**: **2,235 images**
- **Test Split (15%)**: **2,241 images**
- **External Test Set (Held Out)**: **609 leaf images** from *A Citrus Fruits and Leaves Dataset* (never split, never trained on).

---

## 3. Leakage & Split Quality Verification

- **SHA-256 Hash Intersection**: **0 across all partitions (0% leakage)**.
- **Duplicate Group Isolation**: All canonical and associated duplicates map to the same partition.
- **External Test Contamination**: **0 overlapping hashes** between external citrus test images and training/val/test splits.
- **Stratification Fidelity**: Class proportions in Train, Val, and Test match the candidate pool within ±0.2%.

*Full validation audit report:* [`data/reports/split_validation_report.md`](data/reports/split_validation_report.md)

---

## 4. Turmeric Source-Held-Out Evaluation Definition

Because *Turmeric Plant Disease (1)* is a clone of *Advancing AI*, it is excluded from external status. Instead, a rigorous cross-dataset protocol is established between the two independent sources:
- **Shared Classes**: `Healthy` and `Leaf Blotch`.
- **Source A Exclusives**: `Leaf Spot` (evaluated as Out-Of-Distribution anomaly in Protocol 1).
- **Source B Exclusives**: `Dry Leaf` (evaluated as Out-Of-Distribution anomaly in Protocol 2).
- *Full protocol document:* [`data/reports/turmeric_cross_dataset_protocol.md`](data/reports/turmeric_cross_dataset_protocol.md)

---

## 5. Citrus Common-Class External Evaluation Definition

The 609 leaf images from *A Citrus Fruits and Leaves Dataset* map to 5 Lemon classes:
1. `Greening`: 204 images
2. `Black Spot`: 171 images
3. `Citrus Canker`: 163 images
4. `Healthy`: 58 images
5. `Melanose`: 13 images (*LOW-SUPPORT*)
- Evaluation metric: Sub-matrix 5-class transfer accuracy and Macro F1 (labeled explicitly as *"Citrus Common-Class Cross-Dataset Evaluation"*).

---

## 6. Two-Model Crop-Specific Experiment Lock

In accordance with Phase 4A methodological lock, the experiment pipeline uses **two preselected primary models**:
1. **Turmeric Foliar Disease Model**: **`ConvNeXt-Tiny`** (~28.6M params, ImageNet-1K pretrained)
   - Evaluated on: [`turmeric_model_manifest.csv`](data/metadata/turmeric_model_manifest.csv) (1,243 candidate images across 4 classes)
2. **Citrus Foliar Condition Model**: **`EfficientNetV2-S`** (~21.5M params, ImageNet-1K pretrained)
   - Evaluated on: [`citrus_model_manifest.csv`](data/metadata/citrus_model_manifest.csv) (14,911 candidate images across 18 classes)

*(Note: `MobileNetV3-Large`, `DenseNet121`, and `Swin-T` are excluded from the active experimental pipeline and retained solely as related baseline literature).*

**Primary Decider Metric**: **Macro F1** across random seeds **42, 123, 7** (mean ± std).
**Trust Metrics**: Expected Calibration Error (ECE), Temperature Scaling.
**Explainability Metrics**: Grad-CAM pointing game and background masking invariance.

---

## 7. Exact Next Step

**Phase 4 & 4A are complete and locked.**
Proceed to **Phase 5A (Dataset Preprocessing, Transform Pipeline Setup, and Training Skeleton Validation)**.
