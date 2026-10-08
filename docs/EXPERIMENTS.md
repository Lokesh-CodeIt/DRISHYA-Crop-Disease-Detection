# DRISHYA — Experiments & Results

All results below are from **Seed 42** test evaluation using native PyTorch CPU inference.
No multi-seed mean ± SD statistics are available or claimed.

---

## Turmeric — ConvNeXt-Tiny, Seed 42

### Internal Test Set Results

| Metric | Value |
|---|---|
| **Accuracy** | **98.92%** |
| Macro Precision | 0.9921 |
| Macro Recall | 0.9875 |
| Macro F1 | **0.9897** |

### Per-Class Results (Turmeric)

| Class | Precision | Recall | F1 |
|---|---|---|---|
| Healthy | 0.9853 | 1.0000 | 0.9926 |
| Dry Leaf | 1.0000 | 0.9750 | 0.9874 |
| Leaf Blotch | 0.9846 | 0.9846 | 0.9846 |
| Leaf Spot | 0.9985 | 0.9903 | 0.9944 |

### Calibration Results (Turmeric)

- Temperature `T = 0.101698`
- Calibration **inactive** for inference (see `docs/CALIBRATION.md`)
- Validation split had zero classification errors → calibration would cause pathological sharpening

### Cross-Dataset Evaluation (Turmeric)

**Not available.**

A valid source-isolated cross-dataset experiment was not performed for the current combined-pool turmeric model. This is a documented limitation (see `docs/LIMITATIONS.md`).

---

## Citrus — EfficientNetV2-S, Seed 42

### Internal Test Set Results

| Metric | Value |
|---|---|
| **Accuracy** | **92.73%** |
| Macro Precision | 0.8822 |
| Macro Recall | 0.8915 |
| Macro F1 | **0.8863** |

### Per-Class Results (Citrus — Internal)

| Class | Precision | Recall | F1 |
|---|---|---|---|
| Algal_Leaf_Spot | 0.9286 | 0.9429 | 0.9357 |
| Anthracnose | 0.8250 | 0.8250 | 0.8250 |
| Bacterial Blight | 0.8028 | 0.8028 | 0.8028 |
| Black Spot | 0.9259 | 0.9259 | 0.9259 |
| Citrus Canker | 0.9815 | 0.9583 | 0.9697 |
| Citrus Hindu Mite | 0.9750 | 0.9750 | 0.9750 |
| Citrus Leafminer | 0.9067 | 0.8667 | 0.8862 |
| Citrus_Pest | 0.8913 | 0.8913 | 0.8913 |
| Citrus_Scab | 0.9091 | 0.9091 | 0.9091 |
| Curl Leaf | 0.9333 | 0.8750 | 0.9032 |
| Dry Leaf | 0.8571 | 0.9231 | 0.8889 |
| Greening | 0.8500 | 0.9444 | 0.8947 |
| Healthy | 0.9111 | 0.8913 | 0.9011 |
| Lemon_Sooty_Mold | 0.8750 | 0.8750 | 0.8750 |
| Melanose | 0.8929 | 0.8929 | 0.8929 |
| Spider Mites | 0.8684 | 0.8421 | 0.8551 |
| Swallowtail Larval Herbivory (Deficiency) | 0.6667 | 0.6000 | 0.6316 |
| Yellow_Spot | 0.7647 | 0.8125 | 0.7879 |

> *Note: Per-class values are approximate. The canonical source is `docs/book_chapter_results_final.csv`.*

### Calibration Results (Citrus)

| Metric | Before Calibration | After Calibration |
|---|---|---|
| Validation ECE | 0.062936 | **0.032162** |
| Test ECE | 0.058998 | **0.026995** |
| Temperature | — | T = 2.218093 |

Calibration is **active** for Citrus inference.

### Cross-Dataset Evaluation (Citrus)

| Evaluation Set | Accuracy | Macro F1 | Macro F1 Drop |
|---|---|---|---|
| Internal test | 92.73% | 0.8863 | — |
| External (held-out) | 66.01% | 0.4892 | **44.8%** |

Domain shift from training distribution to external field conditions is significant.

---

## Deployment Benchmarks

Measured on CPU (50 timed runs + warm-up).

| Model | File Size | Parameters | Median Latency | Std Dev |
|---|---|---|---|---|
| ConvNeXt-Tiny (Turmeric) | 106.20 MB | 27.82M | 168.39 ms | ±39.46 ms |
| EfficientNetV2-S (Citrus) | 77.92 MB | 20.20M | 336.16 ms | ±22.86 ms |

Deployment runtime is **native PyTorch CPU**. ONNX Runtime is not used in the current production configuration.

---

## Grad-CAM Validation

All 22 supported classes (4 turmeric + 18 citrus) produce valid Grad-CAM overlays.
Validation documented in `docs/explainability_22_class_validation.md` and `docs/explainability_22_class_validation.csv`.

Quantitative lesion localization metrics (IoU, pixel-level segmentation accuracy) are **not available or claimed**.
