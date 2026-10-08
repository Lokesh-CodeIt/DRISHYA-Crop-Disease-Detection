# LeafLens: Two-Model Crop-Specific Experiment Protocol
## Phase 4A Methodological Lock

> [!IMPORTANT]
> **Methodological Decision — Two Preselected Primary Deep Learning Models**:
> Following architectural evaluation and crop-specific diagnostic profiling, the LeafLens experimental pipeline is strictly locked to **two primary deep learning models**:
> 1. **Turmeric Foliar Disease Diagnosis**: **`ConvNeXt-Tiny`**
>    - Dataset: [`turmeric_model_manifest.csv`](data/metadata/turmeric_model_manifest.csv) (1,243 candidate images)
>    - Classes: **4** (`Healthy`, `Leaf Blotch`, `Dry Leaf`, `Leaf Spot`)
> 2. **Citrus Foliar Condition Diagnosis**: **`EfficientNetV2-S`**
>    - Dataset: [`citrus_model_manifest.csv`](data/metadata/citrus_model_manifest.csv) (14,911 candidate images)
>    - Classes: **18** preserved original Lemon Leaf categories (9 disease, 5 pest, 3 deficiency/stress, 1 healthy)
>
> **Excluded from Experimental Training & Benchmarking**:
> `MobileNetV3-Large`, `DenseNet121`, and `Swin-T` are excluded from the active experimental pipeline (documented below solely as related baseline literature).
>
> **Scientific Integrity Mandate**:
> Neither `ConvNeXt-Tiny` nor `EfficientNetV2-S` is claimed to be experimentally superior prior to empirical training and evaluation. They are our **preselected primary models**. All quantitative performance conclusions must derive strictly from empirical experimental results across seeds **42, 123, and 7**.

---

## 1. Primary Model Architecture Specifications

| Parameter | Turmeric Model | Citrus Model |
|-----------|----------------|--------------|
| **Target Crop** | Turmeric (*Curcuma longa*) | Citrus / Lemon (*Citrus limon*) |
| **Model Architecture** | **`ConvNeXt-Tiny`** | **`EfficientNetV2-S`** |
| **Model Family** | Modern Depthwise Pure ConvNet | Neural Architecture Search (Fused-MBConv / MBConv) |
| **Pretrained Weights** | `torchvision.models.ConvNeXt_Tiny_Weights.IMAGENET1K_V1` | `torchvision.models.EfficientNet_V2_S_Weights.IMAGENET1K_V1` |
| **Total Parameters** | ~28.6M | ~21.5M |
| **Candidate Dataset Pool** | **1,243** images | **14,911** images |
| **Target Output Classes** | **4 classes** | **18 classes** |
| **Standard Input Resolution** | $224 \times 224$ px | $384 \times 384$ px (native EfficientNetV2-S) / $224 \times 224$ px fallback |
| **Primary Classifier Head** | `nn.Linear(in_features=768, out_features=4)` | `nn.Linear(in_features=1280, out_features=18)` |
| **Grad-CAM Target Layer** | `model.features[7]` / `stages[3].blocks[2]` | `model.features[7]` |
| **ONNX Runtime Target** | CPU execution (FP32 / INT8 quantized) | CPU execution (FP32 / INT8 quantized) |

---

## 2. Model Profiles & Architectural Rationale

### A. Turmeric Model: `ConvNeXt-Tiny`
- **Dataset Context**: Turmeric foliar dataset has 1,243 clean candidate images across 4 distinct classes.
- **Architectural Match**:
  - Utilizes 7×7 depthwise convolutions and inverted bottleneck channels, providing a large effective receptive field to model elongated leaf margins and localized blotch patches (*Taphrina maculans*) vs. discrete spots (*Colletotrichum curcumae*).
  - Layer Normalization and GELU activations stabilize transfer learning from ImageNet without aggressive parameter divergence on moderate-sized datasets.
  - Native Grad-CAM compatibility generates smooth, continuous activation heatmaps aligned with fungal lesion borders.

### B. Citrus Model: `EfficientNetV2-S`
- **Dataset Context**: Citrus Lemon Leaf dataset has 14,911 clean candidate images across 18 diverse classes spanning diseases, insect pests, and nutritional deficiencies.
- **Architectural Match**:
  - Fused-MBConv layers in early stages preserve fine spatial resolution and high-frequency textures (critical for minute mite stippling, scab excrescences, and sooty mold fungal crusts).
  - Progressive learning and squeeze-and-excitation attention capture complex multi-class boundaries across 18 fine-grained categories.
  - Excellent computational throughput allows training on 14,911 images with controlled memory footprint.

---

## 3. Related Work & Excluded Architectures

For literature comparison and historical context within the research documentation, the following architectures were evaluated during initial architectural scoping but are **explicitly excluded** from the active training pipeline:
1. `MobileNetV3-Large` (~5.4M params): Retained as related work for low-power mobile architectures.
2. `DenseNet121` (~8.0M params): Retained as related work for feature reuse in medical imaging.
3. `Swin-T` (~28.3M params): Retained as related work for vision transformers in agriculture.

None of these three models will be trained or benchmarked in the LeafLens pipeline.

---

## 4. Experiment Protocol & Statistical Rigor

### A. Dataset Split Immutability
All training and validation must strictly use the frozen Phase 4 split CSV manifests:
- Turmeric: [`turmeric_train.csv`](data/metadata/splits/turmeric_train.csv) (870), [`turmeric_val.csv`](data/metadata/splits/turmeric_val.csv) (185), [`turmeric_test.csv`](data/metadata/splits/turmeric_test.csv) (188)
- Citrus: [`citrus_train.csv`](data/metadata/splits/citrus_train.csv) (10,438), [`citrus_val.csv`](data/metadata/splits/citrus_val.csv) (2,236), [`citrus_test.csv`](data/metadata/splits/citrus_test.csv) (2,237)
- External Citrus Test: [`citrus_external_test.csv`](data/metadata/splits/citrus_external_test.csv) (609 leaf images, completely isolated)

### B. Statistical Evaluation Across Seeds
- Training runs will be executed across three fixed random seeds: **42**, **123**, and **7**.
- All reported metrics must be presented as:
  $$\mu \pm \sigma \quad (\text{Mean} \pm \text{Standard Deviation})$$
- No conclusions will be drawn from single-seed experiments.

### C. Standardized Metrics Hierarchy
1. **Primary Metric**: **Macro F1-Score** ($\text{Macro F1} = \frac{1}{C} \sum_{c=1}^C \text{F1}_c$).
2. **Secondary Metrics**: Top-1 Accuracy, Macro Precision, Macro Recall, Per-class F1, Confusion Matrix.
3. **Deployment Metrics**: ONNX Model Size (MB), CPU Inference Latency (ms/image over 100 warm iterations).
4. **Calibration & Trust**: Expected Calibration Error (ECE) before/after Temperature Scaling, Reliability Diagrams.
5. **Explainability**: Grad-CAM pointing game (lesion localization fidelity) and background masking invariance.
6. **Cross-Dataset Generalisation**:
   - Citrus: Common-Class Cross-Dataset Evaluation on 609 external leaf images.
   - Turmeric: Source-held-out transfer evaluation on shared classes (`Healthy` and `Leaf Blotch`) via [`turmeric_external_protocol.csv`](data/metadata/turmeric_external_protocol.csv).
