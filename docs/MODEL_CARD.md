# DRISHYA — Model Cards

---

## Model Card: Turmeric Disease Classifier

### Model Details
| Property | Value |
|---|---|
| Architecture | ConvNeXt-Tiny |
| Framework | PyTorch 2.x |
| Crop | Turmeric (*Curcuma longa*) |
| Number of Classes | 4 |
| Class Names | Healthy, Dry Leaf, Leaf Blotch, Leaf Spot |
| Input Resolution | 224 × 224 × 3 (RGB) |
| Active Seed | 42 |
| Parameters | 27.82M |
| File Size | 106.20 MB |
| Checkpoint Path | `ml/models/turmeric/convnext_tiny/seed_42/best_model.pt` |

### Performance (Seed 42)
| Metric | Value |
|---|---|
| Test Accuracy | 98.92% |
| Macro F1 | 0.9897 |

### Training Data Role
- Trained on curated subset of publicly available turmeric leaf image datasets
- Class distribution balanced across 4 classes
- 70/15/15 stratified split (train/val/test)

### Confidence Policy
- Raw softmax confidence displayed (calibration inactive)
- Predictions below 0.65 confidence are rejected

### Explainability
- Grad-CAM on target layer `features.7`
- Predicted-class logits used for gradient computation

### Intended Use
- Decision support for turmeric leaf disease identification
- Educational and research demonstration

### Non-Intended Use
- Replacement for field expert diagnosis
- Autonomous agricultural management
- Commercial crop insurance without expert review

### Known Limitations
- Cross-dataset generalization not evaluated for current combined-pool model
- Single seed — variance across seeds unknown
- Limited to 4 disease categories

### Deployment Constraints
- CPU-only (no GPU required)
- Input must be a clear photograph of a single turmeric leaf
- Median inference latency: 168.39 ms (±39.46 ms) on CPU

---

## Model Card: Citrus Disease Classifier

### Model Details
| Property | Value |
|---|---|
| Architecture | EfficientNetV2-S |
| Framework | PyTorch 2.x |
| Crop | Citrus (*Citrus* spp.) |
| Number of Classes | 18 |
| Class Names | Algal Leaf Spot, Anthracnose, Bacterial Blight, Black Spot, Citrus Canker, Citrus Hindu Mite, Citrus Leafminer, Citrus Pest, Citrus Scab, Curl Leaf, Dry Leaf, Greening, Healthy, Lemon Sooty Mold, Melanose, Spider Mites, Swallowtail Larval Herbivory (Deficiency), Yellow Spot |
| Input Resolution | 384 × 384 × 3 (RGB) |
| Active Seed | 42 |
| Parameters | 20.20M |
| File Size | 77.92 MB |
| Checkpoint Path | `ml/models/citrus/efficientnet_v2_s/seed_42/best_model.pt` |

### Performance (Seed 42)
| Metric | Value |
|---|---|
| Test Accuracy | 92.73% |
| Macro F1 | 0.8863 |
| External Accuracy | 66.01% |
| External Macro F1 | 0.4892 |

### Training Data Role
- Trained on curated subset of publicly available citrus leaf and fruit disease datasets
- 70/15/15 stratified split
- External test set is fully held-out (not seen during training or validation)

### Confidence Policy
- Temperature-scaled confidence (T = 2.218093) displayed
- Predictions below 0.65 confidence are rejected

### Explainability
- Grad-CAM on target layer `features.7`
- Predicted-class logits used for gradient computation

### Intended Use
- Decision support for citrus leaf disease identification
- Educational and research demonstration

### Non-Intended Use
- Replacement for field expert diagnosis
- Commercial crop management without expert review
- Diagnosis of crop varieties not present in training data

### Known Failure Patterns
- Poor performance on Swallowtail Larval Herbivory (Deficiency): F1 0.63 (lowest class)
- Cross-dataset performance drops significantly: +26% accuracy gap on external data
- Confusion between classes with visually similar lesion patterns (e.g., Greening vs Citrus Leafminer)

### Deployment Constraints
- CPU-only (no GPU required)
- Input must be a clear photograph of a single citrus leaf
- Median inference latency: 336.16 ms (±22.86 ms) on CPU
