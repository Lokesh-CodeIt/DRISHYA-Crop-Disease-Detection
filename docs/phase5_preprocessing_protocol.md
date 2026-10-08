# LeafLens: Phase 5A Preprocessing & Training-Input Protocol
## Document ID: DOC-PHASE5A-PREPROC-01

> **Status**: LOCKED PROTOCOL
> **Scope**: Preprocessing, Data Augmentation, DataLoader Construction, and Input Pipeline Governance ONLY.
> **Associated Phase 4 Split Manifests**: [`data/metadata/splits/`](data/metadata/splits/)

---

## A. Image Loading Governance

1. **Source of Truth**: All training, validation, testing, and external evaluation data loaders must read paths exclusively from the Phase 4 split CSV files:
   - Turmeric Train: [`turmeric_train.csv`](data/metadata/splits/turmeric_train.csv) (870 images)
   - Turmeric Val: [`turmeric_val.csv`](data/metadata/splits/turmeric_val.csv) (185 images)
   - Turmeric Test: [`turmeric_test.csv`](data/metadata/splits/turmeric_test.csv) (188 images)
   - Citrus Train: [`citrus_train.csv`](data/metadata/splits/citrus_train.csv) (10,438 images)
   - Citrus Val: [`citrus_val.csv`](data/metadata/splits/citrus_val.csv) (2,236 images)
   - Citrus Test: [`citrus_test.csv`](data/metadata/splits/citrus_test.csv) (2,237 images)
   - Citrus External: [`citrus_external_test.csv`](data/metadata/splits/citrus_external_test.csv) (609 images)
2. **Strict Prohibition on Directory Scanning**: Training scripts must **NEVER** scan [`DATASET/`](DATASET) directly via `os.walk` or globbing.
3. **Partition Immutability**: Training code must **NEVER** create new splits or alter partition assignments on-the-fly.

---

## B. Image Preprocessing Standard

1. **Color Space Verification**: All images must be unconditionally verified and converted to 3-channel standard sRGB:
   ```python
   image = Image.open(io_stream).convert("RGB")
   ```
2. **Resolution Standardization**:
   - Each crop model receives images resized to match its exact pretrained torchvision feature extractor expectations.
   - Resizing uses bilinear or bicubic interpolation with aspect-ratio preserving logic.
3. **Tensor Normalization**:
   - Pixel intensities are scaled to $[0.0, 1.0]$ via standard float conversion.
   - Channels are standardized using standard ImageNet mean and standard deviation:
     - $\mu = [0.485, 0.456, 0.406]$
     - $\sigma = [0.229, 0.224, 0.225]$

---

## C. Data Augmentation Policy

> [!WARNING]
> **Strict Partition Enforcement**: Data augmentation is permitted **ONLY** on the Training set.
> Validation and Test partitions must **NEVER** undergo random augmentation.

### 1. Training Augmentation Design (Conservative & Agronomically Sound)
In plant pathology computer vision, overly aggressive transformations (e.g. extreme shear, color inversion, heavy solarization, or cutout that deletes small lesions) corrupt diagnostic symptomology. The LeafLens augmentation policy is strictly conservative:
- **Random Horizontal Flip**: $p = 0.5$ (leaves have bilateral visual validity in either orientation).
- **Random Vertical Flip**: $p = 0.5$ (leaves hang or point in varying natural orientations).
- **Subtle Random Rotation**: $[-15^\circ, +15^\circ]$ with reflection or edge padding (preserves orientation without severe corner clipping).
- **Mild Photometric Jitter**:
  - Brightness factor: $\pm 10\%$ (`brightness=0.1`)
  - Contrast factor: $\pm 10\%$ (`contrast=0.1`)
  - Saturation factor: $\pm 10\%$ (`saturation=0.1`)
  - Hue factor: **$0.0$ (Strictly Disabled)** — changing green to red/blue alters necrotic chlorosis and falsifies disease signatures!

### 2. Validation & Testing Transformation (Deterministic)
- Strictly deterministic: `Resize` $\to$ `ToTensor` $\to$ `Normalize`.
- Zero stochasticity, zero random cropping, zero random erasing.

---

## D. Class Handling & Taxonomy Integrity

1. **Turmeric (4 Classes)**:
   - Index 0: `Dry Leaf`
   - Index 1: `Healthy`
   - Index 2: `Leaf Blotch`
   - Index 3: `Leaf Spot`
   - **Non-Merge Mandate**: `Leaf Spot` (*Colletotrichum curcumae*) and `Leaf Blotch` (*Taphrina maculans*) must remain completely separate classes.
2. **Citrus (18 Classes)**:
   - Preserves all 18 original Lemon Leaf labels in alphabetical order (indices 0 to 17).
   - Zero label renaming, zero class deletion, zero class collapsing.
   - Condition type metadata (`disease`, `pest`, `deficiency_or_stress`, `healthy`) is carried as an auxiliary diagnostic property.

---

## E. Reproducibility & Seed Protocol

All data loading, worker initialization, and model weight initialization must be deterministic:
- Seeds: **42** (primary), **123** (secondary), **7** (tertiary).
- Deterministic worker seeding in PyTorch DataLoaders:
  ```python
  def seed_worker(worker_id):
      worker_seed = torch.initial_seed() % 2**32
      np.random.seed(worker_seed)
      random.seed(worker_seed)
  ```
- PyTorch CUDNN determinism: `torch.backends.cudnn.deterministic = True`, `torch.backends.cudnn.benchmark = False`.

---

## F. Data Leakage Prevention Guarantees

1. **No Test Augmentation**: No random transforms on validation or test sets.
2. **No Duplicate Leakage**: Verified in Phase 4 audit — 0 hash overlap between train, val, test.
3. **No External Contamination**: The 609 leaf images in `citrus_external_test.csv` are strictly quarantined from all training loops.
4. **No Raw Directory Scanning**: Every image loaded during training traces back to an explicit `image_id` in the split manifest.

---

## G. Model-Specific Preprocessing Specifications

### 1. Turmeric: `ConvNeXt-Tiny`
- **PyTorch Model**: `torchvision.models.convnext_tiny(weights=ConvNeXt_Tiny_Weights.IMAGENET1K_V1)`
- **Input Dimensions**: $3 \times 224 \times 224$
- **Expected Transforms**:
  - Train: `RandomResizedCrop(224, scale=(0.8, 1.0))` / `Resize((224, 224))` + `RandomHorizontalFlip()` + `RandomVerticalFlip()` + `RandomRotation(15)` + `ColorJitter(0.1, 0.1, 0.1, 0.0)` + `ToTensor()` + `Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`
  - Val/Test: `Resize((224, 224))` + `ToTensor()` + `Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`
- **Output Head**: `nn.Linear(in_features=768, out_features=4)`

### 2. Citrus: `EfficientNetV2-S`
- **PyTorch Model**: `torchvision.models.efficientnet_v2_s(weights=EfficientNet_V2_S_Weights.IMAGENET1K_V1)`
- **Input Dimensions**: $3 \times 384 \times 384$ (native EfficientNetV2-S resolution)
- **Expected Transforms**:
  - Train: `Resize((384, 384))` + `RandomHorizontalFlip()` + `RandomVerticalFlip()` + `RandomRotation(15)` + `ColorJitter(0.1, 0.1, 0.1, 0.0)` + `ToTensor()` + `Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`
  - Val/Test: `Resize((384, 384))` + `ToTensor()` + `Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`
- **Output Head**: `nn.Linear(in_features=1280, out_features=18)`
