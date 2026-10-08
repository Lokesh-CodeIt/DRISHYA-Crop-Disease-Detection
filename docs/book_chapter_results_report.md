# DRISHYA — Book Chapter Results Report
**Project:** `.`
**Generated:** 2026-10-07 (UTC)
**Method:** All values extracted from actual trained model artifacts only. No value is estimated or invented.

> [!IMPORTANT]
> Every number in this report traces to a specific file path and computation method listed in the "Source" column. The companion machine-readable files are:
> - [`docs/book_chapter_results.json`](docs/book_chapter_results.json)
> - [`docs/book_chapter_results.csv`](docs/book_chapter_results.csv)
> - [`docs/book_chapter_reliability_data.json`](docs/book_chapter_reliability_data.json)

---

## Seed Availability

| Crop | Seeds with Completed Checkpoints | Seeds Planned but Not Completed |
|---|---|---|
| Turmeric | **42 only** | 123, 7 |
| Citrus | **42 only** | 123, 7 |

> [!WARNING]
> Mean ± SD across 3 seeds **cannot be computed** for either crop. Only seed=42 results are available. Do NOT fabricate multi-seed statistics.

---

## TABLE 7.1 — Overall Model Performance (Test Set, Seed 42)

| Crop | Architecture | Seed | Split | N | Accuracy | Macro F1 | Macro Precision | Macro Recall |
|---|---|---|---|---|---|---|---|---|
| Turmeric | ConvNeXt-Tiny | 42 | test | 186 | **98.92%** | **0.9897** | **0.9921** | **0.9875** |
| Citrus | EfficientNetV2-S | 42 | test | 2,241 | **92.73%** | **0.8863** | **0.8822** | **0.8915** |

**Publication-ready rounded values:**
- Turmeric: Accuracy = 98.9%, Macro F1 = 0.990, Precision = 0.992, Recall = 0.988
- Citrus: Accuracy = 92.7%, Macro F1 = 0.886, Precision = 0.882, Recall = 0.892

**Source:** `ml/calibration/cache/{crop}_test_logits.npz` — logits cached during calibration pipeline, labels from split CSVs, sklearn `accuracy_score` / `f1_score` / `precision_score` / `recall_score` with `average="macro"`, `zero_division=0`.

> [!NOTE]
> Mean ± SD column: **NOT AVAILABLE** — seeds 123 and 7 checkpoints absent.

---

## TABLE 7.2 — Turmeric Per-Class Classification Report (Test Set, Seed 42)

Model: ConvNeXt-Tiny | Split: `turmeric_test.csv` (N=186) | Temperature T=1.0 (uncalibrated predictions)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Dry Leaf | **1.0000** | **1.0000** | **1.0000** | 31 |
| Healthy | **0.9839** | **1.0000** | **0.9919** | 61 |
| Leaf Blotch | **0.9846** | **0.9846** | **0.9846** | 65 |
| Leaf Spot | **1.0000** | **0.9655** | **0.9825** | 29 |
| **Macro avg** | **0.9921** | **0.9875** | **0.9897** | **186** |

**Source:** `ml/calibration/cache/turmeric_test_logits.npz`
**Calculation:** `sklearn.metrics.classification_report` equivalent — `precision_score(average=None)`, `recall_score(average=None)`, `f1_score(average=None)`, `np.bincount(labels)`

---

## TABLE 7.3 — Citrus Per-Class Classification Report (Test Set, Seed 42)

Model: EfficientNetV2-S | Split: `citrus_test.csv` (N=2,241) | Temperature T=1.0

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Algal_Leaf_Spot | **1.0000** | **1.0000** | **1.0000** | 126 |
| Anthracnose | **0.8473** | **0.8810** | **0.8638** | 126 |
| Bacterial Blight | **0.4545** | **0.5263** | **0.4878** | 19 |
| Black Spot | **0.9706** | **0.9429** | **0.9565** | 105 |
| Citrus Canker | **0.9420** | **0.9378** | **0.9399** | 225 |
| Citrus Hindu Mite | **0.8953** | **0.9506** | **0.9222** | 81 |
| Citrus Leafminer | **0.8807** | **0.8205** | **0.8496** | 117 |
| Citrus_Pest | **1.0000** | **1.0000** | **1.0000** | 82 |
| Citrus_Scab | **1.0000** | **1.0000** | **1.0000** | 50 |
| Curl Leaf | **0.9068** | **0.9106** | **0.9087** | 235 |
| Dry Leaf | **0.7333** | **0.7333** | **0.7333** | 30 |
| Greening | **0.8959** | **0.9198** | **0.9077** | 262 |
| Healthy | **0.9751** | **0.9592** | **0.9671** | 245 |
| Lemon_Sooty_Mold | **1.0000** | **1.0000** | **1.0000** | 239 |
| Melanose | **0.6333** | **0.6786** | **0.6552** | 28 |
| Spider Mites | **0.8500** | **0.9444** | **0.8947** | 18 |
| Swallowtail Larval Herbivory (Deficiency) | **0.8951** | **0.8421** | **0.8678** | 152 |
| Yellow_Spot | **1.0000** | **1.0000** | **1.0000** | 101 |
| **Macro avg** | **0.8822** | **0.8915** | **0.8863** | **2,241** |

**Source:** `ml/calibration/cache/citrus_test_logits.npz`

> [!NOTE]
> Bacterial Blight (N=19) and Melanose (N=28) have the weakest F1 scores (0.49 and 0.66 respectively), consistent with their low support counts in the test split.

---

## TABLE 7.4 — Cross-Dataset Generalisation

### Turmeric

| Protocol | In-Dataset Macro F1 | Cross-Dataset Macro F1 | % Drop |
|---|---|---|---|
| TURM_CROSS_B_TO_A | **NOT AVAILABLE** | **NOT AVAILABLE** | **NOT AVAILABLE** |
| TURM_CROSS_A_TO_B | **NOT AVAILABLE** | **NOT AVAILABLE** | **NOT AVAILABLE** |

**Reason not available:** Per [`turmeric_cross_dataset_protocol.md`](data/reports/turmeric_cross_dataset_protocol.md), valid cross-dataset evaluation requires two separate source-isolated training experiments:
1. **TURM_CROSS_B_TO_A**: Train on Source B (Advancing AI; Dry Leaf+Healthy+Leaf Blotch), test on Source A shared classes (Healthy=213, Leaf Blotch=238).
2. **TURM_CROSS_A_TO_B**: Train on Source A (Turmeric Leaf Disease; Healthy+Leaf Blotch+Leaf Spot), test on Source B shared classes (Healthy=197, Leaf Blotch=199).

The current model is trained on the **combined** 4-class pool. Using it as a cross-dataset result would be scientifically invalid.

### Citrus

| Evaluation | Accuracy | Macro F1 | N | Dataset |
|---|---|---|---|---|
| In-Dataset (18-class test set) | 92.73% | **0.8863** | 2,241 | Internal `citrus_test.csv` |
| Cross-Dataset (5-class submatrix) | **66.01%** | **0.4892** | 609 | *A Citrus Fruits and Leaves Dataset* |
| **F1 Drop** | — | **−44.8%** | — | — |

**Cross-Dataset Per-Class Breakdown (5-class submatrix):**

| Class | Precision | Recall | F1-Score | Support | Note |
|---|---|---|---|---|---|
| Black Spot | 0.7667 | 0.2690 | **0.3983** | 171 | Low recall — visual domain shift |
| Citrus Canker | 0.9325 | 0.9325 | **0.9325** | 163 | Strong transfer ✅ |
| Greening | 0.5497 | 0.9216 | **0.6886** | 204 | High recall, low precision |
| Healthy | 0.9412 | 0.2759 | **0.4267** | 58 | Severe recall drop |
| Melanose | 0.0000 | 0.0000 | **0.0000** | 13 | Complete failure — likely domain/appearance mismatch |

**Source:** `data/metadata/splits/citrus_external_test.csv` (609 images from *A Citrus Fruits and Leaves Dataset for Detection and Classification of Citrus Diseases through Machine Learning*). Full EfficientNetV2-S forward pass on all 609 images; 5-class logit submatrix evaluated.

> [!WARNING]
> Melanose (N=13) has zero F1 on the external set despite 0.655 in-distribution F1. This is likely due to the very small external support (13 samples) and domain shift in Melanose appearance between datasets. The 44.8% F1 drop overall is a genuine cross-domain generalisation challenge, not a data processing error.

---

## TABLE 7.5 — Confidence Calibration (Temperature Scaling)

| Crop | Val ECE (before) | Val ECE (after) | Test ECE (before) | Learned T | Test ECE (after) | ECE Reduction |
|---|---|---|---|---|---|---|
| Turmeric | 0.0064 | 0.0000 | **0.0052** | **0.1017** | **0.0107** | −104.8%* |
| Citrus | 0.0629 | 0.0322 | **0.0590** | **2.2181** | **0.0270** | **54.2%** |

*Turmeric note: The model is already very well-calibrated (ECE=0.005 before calibration). The learned T=0.1017 sharpens probabilities further on validation but slightly degrades test ECE — this is expected for a near-perfectly accurate model (98.9% test accuracy) where temperature scaling overfits the tiny calibration gap in the 187-sample val split.

**Source:** `ml/calibration/calibration_report.json`, `ml/calibration/turmeric_temperature.json`, `ml/calibration/citrus_temperature.json`
**Method:** L-BFGS minimization of Negative Log Likelihood on **validation split only**. Test split evaluated strictly post-fit (never used to tune T). 15-bin ECE (equal-width), `n_bins=15`.

---

## Figure 7.1 — Reliability Diagram Data (10-bin, Publication Standard)

Source: `ml/calibration/cache/*_test_logits.npz` — computed from real cached logits.

### Turmeric Test Set

| | ECE (10-bin) |
|---|---|
| Uncalibrated (T=1.0) | **0.004682** |
| Calibrated (T=0.1017) | **0.010745** |

### Citrus Test Set

| | ECE (10-bin) |
|---|---|
| Uncalibrated (T=1.0) | **0.058663** |
| Calibrated (T=2.2181) | **0.022962** |

**Full 10-bin data** (bin-by-bin confidence, accuracy, gap, sample count) available in:
[`docs/book_chapter_reliability_data.json`](docs/book_chapter_reliability_data.json)

**15-bin data** (used in calibration pipeline): `ml/calibration/reliability_data.json`

---

## TABLE 7.6 — Explainability Metrics

| Metric | Turmeric | Citrus |
|---|---|---|
| Grad-CAM attention (% in lesion) | NOT AVAILABLE | NOT AVAILABLE |
| Grad-CAM++ attention (% in lesion) | NOT AVAILABLE | NOT AVAILABLE |
| Background-masking ΔAccuracy | NOT AVAILABLE | NOT AVAILABLE |

**Reason:** No pixel-level lesion ground truth annotations exist. No pointing-game experiment has been executed. Grad-CAM++ is not implemented in the codebase. The `GradCAMExplanation` schema exists in the API layer but no quantitative localization metric has been run.

**What is needed to fill this table:**
1. Annotate lesion bounding boxes for ≥100 test images per crop.
2. Implement Grad-CAM++ hook in `backend/app/ml/model_builder.py`.
3. Run pointing-game: fraction of test images where `argmax(CAM heatmap)` falls inside the annotated lesion bounding box.
4. Run background-masking: zero all pixels *not* highlighted by the CAM, measure ΔAccuracy vs. original.

---

## TABLE 7.7 — Deployment Characteristics

| Crop | Architecture | Checkpoint Size | Parameters | Runtime | CPU Inference (median) | CPU Inference (std) | Runs |
|---|---|---|---|---|---|---|---|
| Turmeric | ConvNeXt-Tiny | **106.20 MB** | **27.82M** | PyTorch CPU | **168.39 ms** | ±39.46 ms | 50 |
| Citrus | EfficientNetV2-S | **77.92 MB** | **20.20M** | PyTorch CPU | **336.16 ms** | ±22.86 ms | 50 |

**Notes:**
- Runtime is **native PyTorch CPU** (`torch.no_grad()`, single image, 1×3×H×W tensor). ONNX Runtime is **not used** in the current implementation.
- Input resolution: Turmeric = 224×224 px, Citrus = 384×384 px (explains latency difference).
- Benchmark machine: same Windows machine used for all experiments (Intel CPU, no GPU).
- 5 warm-up runs before 50 timed runs. Median reported (robust to JIT warm-up outliers).

**Source:** `ml/models/turmeric/convnext_tiny/seed_42/best_model.pt` (file size via `Path.stat().st_size`), `sum(p.numel() for p in model.parameters())`, `time.perf_counter()` × 50 runs.

---

## TABLE 7.8 — Comparison with Published Studies

> [!CAUTION]
> Only "This work" rows are filled from our experiments. All published-study values must come from their original papers — do NOT invent or alter those numbers.

| Study | Crop/Task | Method | Accuracy | Macro F1 |
|---|---|---|---|---|
| *(published literature — preserve from chapter draft)* | — | — | — | — |
| **This work (Turmeric)** | Turmeric (4-class) | ConvNeXt-Tiny + Temperature Scaling | **98.92%** | **0.9897** |
| **This work (Citrus)** | Citrus (18-class) | EfficientNetV2-S + Temperature Scaling | **92.73%** | **0.8863** |

---

## NOT AVAILABLE — Values That Cannot Be Filled From Current Experiments

| Table | Value | Reason | Experiment Required |
|---|---|---|---|
| 7.1 | Turmeric 3-seed Mean ± SD | Seeds 123, 7 not trained | Train ConvNeXt-Tiny for turmeric seeds 123 and 7 |
| 7.1 | Citrus 3-seed Mean ± SD | Seeds 123, 7 not trained | Train EfficientNetV2-S for citrus seeds 123 and 7 |
| 7.4 | Turmeric cross-dataset F1 | Combined-pool model cannot serve as source-isolated experiment | Run TURM_CROSS_B_TO_A and TURM_CROSS_A_TO_B (separate training runs on single source each) |
| 7.6 | All Grad-CAM/Grad-CAM++ metrics | No lesion GT, Grad-CAM++ not implemented, no pointing-game run | Annotate test images + implement Grad-CAM++ + run pointing-game protocol |

---

## Data Provenance Summary

| Artifact | Path | Role |
|---|---|---|
| Turmeric logit cache | `ml/calibration/cache/turmeric_test_logits.npz` | Source for all turmeric test metrics |
| Citrus logit cache | `ml/calibration/cache/citrus_test_logits.npz` | Source for all citrus test metrics |
| Turmeric temperature | `ml/calibration/turmeric_temperature.json` | T=0.101698, all calibration metrics |
| Citrus temperature | `ml/calibration/citrus_temperature.json` | T=2.218093, all calibration metrics |
| Calibration report | `ml/calibration/calibration_report.json` | ECE before/after, NLL, val+test splits |
| Reliability diagram data | `ml/calibration/reliability_data.json` | 15-bin bin-level data |
| Turmeric checkpoint | `ml/models/turmeric/convnext_tiny/seed_42/best_model.pt` | File size, params, CPU timing |
| Citrus checkpoint | `ml/models/citrus/efficientnet_v2_s/seed_42/best_model.pt` | File size, params, CPU timing |
| Turmeric test split | `data/metadata/splits/turmeric_test.csv` | 186 images, 4 classes |
| Citrus test split | `data/metadata/splits/citrus_test.csv` | 2,241 images, 18 classes |
| Citrus external test | `data/metadata/splits/citrus_external_test.csv` | 609 images, 5 classes (cross-dataset) |
| Cross-dataset protocol | `data/reports/turmeric_cross_dataset_protocol.md` | Defines valid turmeric cross-dataset protocol |
