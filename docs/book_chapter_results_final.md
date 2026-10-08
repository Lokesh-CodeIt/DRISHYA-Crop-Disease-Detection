# DRISHYA — Final Book Chapter Results Reconciliation Package

**Project Root:** `.`  
**Reconciliation Date:** 2026-10-07  
**Verification Method:** 100% verified against real repository checkpoints and cached evaluation artifacts. No interpolated, assumed, or fabricated numbers.

---

## 1. Executive Summary & Experiment Reconciliation

A rigorous forensic inspection of the physical checkpoint directory (`ml/models/`) was conducted. The results reconcile the discrepancies between earlier project notes and physical reality:

| Crop | Architecture | Completed Seeds (Physical Checkpoints) | Missing / Uncompleted Seeds | Multi-Seed Policy |
|---|---|---|---|---|
| **Turmeric** | ConvNeXt-Tiny | **Seed 42 only** (`ml/models/turmeric/convnext_tiny/seed_42/best_model.pt`) | Seeds 123, 7 | **Single-seed reporting (Seed 42)**; Mean ± SD marked `NOT AVAILABLE` |
| **Citrus** | EfficientNetV2-S | **Seed 42 only** (`ml/models/citrus/efficientnet_v2_s/seed_42/best_model.pt`) | Seeds 123, 7 | **Single-seed reporting (Seed 42)**; Mean ± SD marked `NOT AVAILABLE` |

> [!IMPORTANT]
> **Strict Scientific Integrity Rules Applied:**
> 1. **Multi-Seed Rule:** Because seeds 123 and 7 do not physically exist, **no multi-seed mean or standard deviation has been fabricated**. Only Seed 42 is reported.
> 2. **Cross-Dataset Rule:** The combined-pool Turmeric model is **not** used as a cross-dataset experiment. Turmeric cross-dataset evaluation is honestly reported as `NOT AVAILABLE` pending source-isolated training. Citrus cross-dataset generalisation uses the genuine 609-image external test set.
> 3. **Calibration Honesty Rule:** Post-hoc temperature scaling improved Citrus calibration (54.24% ECE reduction), but **worsened** Turmeric test calibration (from 0.0052 to 0.0107). This nuance is documented transparently.
> 4. **Explainability Rule:** Table 7.6 Grad-CAM quantitative metrics are marked `NOT AVAILABLE` because pixel-level lesion ground truth annotations and pointing-game experiments do not exist.

---

## TABLE 7.1 — Overall Model Performance (Test Split, Seed 42)

| Crop | Architecture | Seed | Split | N | Accuracy | Macro F1 | Macro Precision | Macro Recall | 3-Seed Mean ± SD |
|---|---|---|---|---|---|---|---|---|---|
| **Turmeric** | ConvNeXt-Tiny | 42 | Test | 186 | **98.92%** | **0.9897** | **0.9921** | **0.9875** | *NOT AVAILABLE — REQUIRED EXPERIMENT NOT COMPLETED* |
| **Citrus** | EfficientNetV2-S | 42 | Test | 2,241 | **92.73%** | **0.8863** | **0.8822** | **0.8915** | *NOT AVAILABLE — REQUIRED EXPERIMENT NOT COMPLETED* |

**Publication-Ready Summary:**
- **Turmeric (ConvNeXt-Tiny):** Accuracy = **98.92%**, Macro F1 = **0.9897**, Macro Precision = **0.9921**, Macro Recall = **0.9875** (N = 186).
- **Citrus (EfficientNetV2-S):** Accuracy = **92.73%**, Macro F1 = **0.8863**, Macro Precision = **0.8822**, Macro Recall = **0.8915** (N = 2,241).
- **Source Artifacts:** `ml/calibration/cache/turmeric_test_logits.npz` and `ml/calibration/cache/citrus_test_logits.npz`.

---

## TABLE 7.2 — Turmeric Per-Class Classification Report (Test Split, Seed 42)

Model: **ConvNeXt-Tiny** | Input Resolution: **224 × 224** | Split: `turmeric_test.csv` (N = 186)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Dry Leaf | **1.0000** | **1.0000** | **1.0000** | 31 |
| Healthy | **0.9839** | **1.0000** | **0.9919** | 61 |
| Leaf Blotch | **0.9846** | **0.9846** | **0.9846** | 65 |
| Leaf Spot | **1.0000** | **0.9655** | **0.9825** | 29 |
| **Macro Average** | **0.9921** | **0.9875** | **0.9897** | **186** |

**Source:** `ml/calibration/cache/turmeric_test_logits.npz`  
**Method:** Uncalibrated argmax logits, `sklearn.metrics.classification_report` formulas with `zero_division=0`.

---

## TABLE 7.3 — Citrus Per-Class Classification Report (Test Split, Seed 42)

Model: **EfficientNetV2-S** | Input Resolution: **384 × 384** | Split: `citrus_test.csv` (N = 2,241)

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
| **Macro Average** | **0.8822** | **0.8915** | **0.8863** | **2,241** |

**Source:** `ml/calibration/cache/citrus_test_logits.npz`  
**Method:** Uncalibrated argmax logits, `sklearn.metrics.classification_report` formulas with `zero_division=0`.

---

## TABLE 7.4 — Cross-Dataset Generalisation

### Turmeric
| Evaluation | In-Dataset Macro F1 | Cross-Dataset Macro F1 | Relative Drop | Status |
|---|---|---|---|---|
| Source Isolation Protocol | *N/A* | *N/A* | *N/A* | **NOT AVAILABLE — REQUIRED EXPERIMENT NOT COMPLETED** |

> [!NOTE]
> **Scientific Integrity Justification:** The active Turmeric classifier was trained on a combined dataset pool (Source A + Source B). Per `data/reports/turmeric_cross_dataset_protocol.md`, valid cross-dataset evaluation mandates training strictly on Source A and testing on Source B, and vice-versa. Evaluating the combined-pool model on either source would constitute data leakage.

### Citrus
| Evaluation | Dataset Split | N | Accuracy | Macro F1 | Relative Drop |
|---|---|---|---|---|---|
| In-Dataset Test | `data/metadata/splits/citrus_test.csv` (18 classes) | 2,241 | **92.73%** | **0.8863** | — |
| Cross-Dataset External Test | `data/metadata/splits/citrus_external_test.csv` (5 shared classes) | 609 | **66.01%** | **0.4892** | **−44.81%** |

**Per-Class Performance on External Citrus Dataset (N = 609, 5 Shared Classes):**

| Class | Precision | Recall | F1-Score | Support | Clinical Observation |
|---|---|---|---|---|---|
| Black Spot | 0.7667 | 0.2690 | **0.3983** | 171 | Substantial visual domain shift in lesion presentation |
| Citrus Canker | 0.9325 | 0.9325 | **0.9325** | 163 | Robust cross-domain transfer |
| Greening | 0.5497 | 0.9216 | **0.6886** | 204 | High sensitivity, elevated false alarm rate |
| Healthy | 0.9412 | 0.2759 | **0.4267** | 58 | Significant background/lighting domain shift |
| Melanose | 0.0000 | 0.0000 | **0.0000** | 13 | Complete transfer failure due to extreme scarcity and distinct lesion morphology |

**Source:** `data/metadata/splits/citrus_external_test.csv` evaluated on EfficientNetV2-S forward pass.

---

## TABLE 7.5 — Confidence Calibration (Post-Hoc Temperature Scaling)

Methodology: Temperature Scaling (Guo et al., 2017) optimized via L-BFGS on **validation Negative Log Likelihood (NLL) only**. Test splits evaluated strictly post-fit (zero data leakage).

| Crop | Split | N | ECE (Before) | Learned Temperature $T$ | ECE (After) | Relative ECE Change | NLL (Before $\to$ After) | Brier (Before $\to$ After) | Calibration Outcome |
|---|---|---|---|---|---|---|---|---|---|
| **Turmeric** | Validation | 187 | 0.0064 | **0.1017** | 0.0000 | −100.00% | 0.0066 $\to$ 0.0000 | 0.0008 $\to$ 0.0000 | Perfect val convergence |
| **Turmeric** | **Test** | 186 | **0.0052** | **0.1017** | **0.0107** | **+104.78% (worsened)** | 0.0425 $\to$ 0.3176 | 0.0176 $\to$ 0.0215 | **Calibration Worsened Test ECE** |
| **Citrus** | Validation | 2,235 | 0.0629 | **2.2181** | 0.0322 | −48.90% | 0.4722 $\to$ 0.2772 | 0.1360 $\to$ 0.1167 | Substantial val improvement |
| **Citrus** | **Test** | 2,241 | **0.0590** | **2.2181** | **0.0270** | **−54.24% (improved)** | 0.4507 $\to$ 0.2700 | 0.1314 $\to$ 0.1144 | **Calibration Substantially Improved Test ECE** |

> [!IMPORTANT]
> **Critical Analytical Insight on Calibration:**
> - **Citrus:** Temperature scaling with $T = 2.2181$ achieved strong success, reducing test ECE by **54.24%** (from 0.0590 to 0.0270), test NLL by **40.1%**, and test Brier score by **12.9%**. The temperature successfully softened overconfident predictions.
> - **Turmeric:** The uncalibrated Turmeric model is already exceptionally well-calibrated in-distribution ($ECE = 0.0052$). Because the 187-sample validation set had 100% accuracy, L-BFGS pushed $T$ down to $0.1017$ to minimize log loss toward 0. Applying this sharp scaling to the test set overconfidently penalized test mistakes, doubling test ECE to $0.0107$. Therefore, DRISHYA explicitly documents that **temperature scaling is beneficial for complex, multi-class regimes (Citrus) but should not be blindly applied to near-saturated classifiers (Turmeric)**.

---

## FIGURE 7.1 — Reliability Diagram Data (Publication 10-Bin Standard)

Source: `ml/calibration/cache/{crop}_test_logits.npz` | Test Splits

### Turmeric Test Set (N = 186)
- **Uncalibrated ($T = 1.0$):** $ECE_{10\text{-bin}} = \mathbf{0.0047}$
- **Calibrated ($T = 0.1017$):** $ECE_{10\text{-bin}} = \mathbf{0.0107}$

| Bin Index | Confidence Range | Uncalibrated Samples | Uncalibrated Gap | Calibrated Samples | Calibrated Gap |
|---|---|---|---|---|---|
| 0–8 | [0.0, 0.9) | 0 | 0.0000 | 0 | 0.0000 |
| 9 | [0.9, 1.0] | 186 | 0.0047 | 186 | 0.0107 |

### Citrus Test Set (N = 2,241)
- **Uncalibrated ($T = 1.0$):** $ECE_{10\text{-bin}} = \mathbf{0.0587}$
- **Calibrated ($T = 2.2181$):** $ECE_{10\text{-bin}} = \mathbf{0.0230}$

| Bin Index | Confidence Range | Uncalibrated Samples | Uncalibrated Accuracy | Uncalibrated Confidence | Uncalibrated Gap | Calibrated Samples | Calibrated Accuracy | Calibrated Confidence | Calibrated Gap |
|---|---|---|---|---|---|---|---|---|---|
| 0 | [0.0, 0.1) | 0 | — | — | 0.0000 | 0 | — | — | 0.0000 |
| 1 | [0.1, 0.2) | 0 | — | — | 0.0000 | 0 | — | — | 0.0000 |
| 2 | [0.2, 0.3) | 0 | — | — | 0.0000 | 1 | 0.0000 | 0.2718 | 0.2718 |
| 3 | [0.3, 0.4) | 2 | 0.5000 | 0.3547 | 0.1453 | 11 | 0.1818 | 0.3642 | 0.1824 |
| 4 | [0.4, 0.5) | 6 | 0.3333 | 0.4578 | 0.1245 | 39 | 0.4103 | 0.4589 | 0.0486 |
| 5 | [0.5, 0.6) | 12 | 0.5833 | 0.5516 | 0.0317 | 64 | 0.5312 | 0.5542 | 0.0230 |
| 6 | [0.6, 0.7) | 15 | 0.5333 | 0.6554 | 0.1221 | 108 | 0.6019 | 0.6548 | 0.0529 |
| 7 | [0.7, 0.8) | 48 | 0.6250 | 0.7570 | 0.1320 | 185 | 0.7676 | 0.7547 | 0.0129 |
| 8 | [0.8, 0.9) | 134 | 0.7910 | 0.8588 | 0.0678 | 413 | 0.8644 | 0.8569 | 0.0075 |
| 9 | [0.9, 1.0] | 2,024 | 0.9476 | 0.9959 | **0.0483** | 1,420 | 0.9845 | 0.9632 | **0.0213** |

---

## TABLE 7.6 — Explainability Metrics

| Metric | Turmeric (ConvNeXt-Tiny) | Citrus (EfficientNetV2-S) |
|---|---|---|
| Grad-CAM attention (% in lesion) | **NOT AVAILABLE** | **NOT AVAILABLE** |
| Grad-CAM++ attention (% in lesion) | **NOT AVAILABLE** | **NOT AVAILABLE** |
| Background-masking $\Delta$Accuracy | **NOT AVAILABLE** | **NOT AVAILABLE** |

**Reason:** No pixel-level lesion ground-truth annotations exist in the dataset repository. Grad-CAM++ is not implemented in the model builder. Pointing-game and perturbation experiments have not been conducted.  
**Required Experiment:** Annotate lesion ground-truth bounding boxes / segmentations on $\ge 100$ test images per crop, implement Grad-CAM++, and execute the pointing-game protocol.

---

## TABLE 7.7 — Deployment Characteristics

Benchmarked on **Intel CPU (Windows x64)** under **native PyTorch CPU** (`torch.no_grad()`, single image batch, 5 warmup runs, 50 timed iterations).

| Crop | Architecture | Input Resolution | Checkpoint File Size | Total Parameters | Millions of Parameters | CPU Inference Time (Median) | CPU Inference Time (Std) | Timed Runs |
|---|---|---|---|---|---|---|---|---|
| **Turmeric** | ConvNeXt-Tiny | 224 × 224 | **106.20 MB** | 27,823,204 | **27.82 M** | **168.39 ms** | ±39.46 ms | 50 |
| **Citrus** | EfficientNetV2-S | 384 × 384 | **77.92 MB** | 20,200,546 | **20.20 M** | **336.16 ms** | ±22.86 ms | 50 |

**Sources:**
- Turmeric Checkpoint: `ml/models/turmeric/convnext_tiny/seed_42/best_model.pt` (111,357,831 bytes = 106.20 MB)
- Citrus Checkpoint: `ml/models/citrus/efficientnet_v2_s/seed_42/best_model.pt` (81,704,671 bytes = 77.92 MB)

---

## TABLE 7.8 — Comparison with Published Studies

*Note: Published literature values from external studies are preserved verbatim from the chapter draft. Only "This work" rows are populated from physical repository artifacts.*

| Study | Crop / Task | Method | Accuracy | Macro F1 |
|---|---|---|---|---|
| *(Preserved from literature)* | Citrus / Turmeric | *(Published references)* | *(Per published paper)* | *(Per published paper)* |
| **This work (Turmeric)** | Turmeric (4-class) | ConvNeXt-Tiny + Post-Hoc Analysis | **98.92%** | **0.9897** |
| **This work (Citrus)** | Citrus (18-class) | EfficientNetV2-S + Temperature Scaling | **92.73%** | **0.8863** |

---

## Complete Audit of Unavailable Values

| Table | Metric | Crop | Missing Requirement | Required Action |
|---|---|---|---|---|
| 7.1 | 3-Seed Mean ± SD | Turmeric | Seeds 123 and 7 not trained | Train ConvNeXt-Tiny with seed 123 and seed 7 |
| 7.1 | 3-Seed Mean ± SD | Citrus | Seeds 123 and 7 not trained | Train EfficientNetV2-S with seed 123 and seed 7 |
| 7.4 | Cross-Dataset Macro F1 & Drop | Turmeric | Source-isolated training runs absent | Run TURM_CROSS_B_TO_A and TURM_CROSS_A_TO_B source-isolated training protocols |
| 7.6 | All Grad-CAM / Grad-CAM++ Metrics | Both | No lesion ground truth masks; Grad-CAM++ not implemented | Annotate lesion masks; implement Grad-CAM++; run pointing game and masking ablation |

---

## File Deliverables Reference

The following three authoritative files have been generated:
1. [`docs/book_chapter_results_final.csv`](docs/book_chapter_results_final.csv) — Complete table-ready CSV with raw and publication-rounded columns, source artifacts, and explicit status markers.
2. [`docs/book_chapter_results_final.json`](docs/book_chapter_results_final.json) — Machine-readable JSON database with full floating-point precision, full bin data for Figure 7.1, and exhaustive metadata.
3. [`docs/book_chapter_results_final.md`](docs/book_chapter_results_final.md) — Publication-ready markdown report with formatted tables and analytical discussion.
