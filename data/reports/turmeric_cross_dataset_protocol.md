# LeafLens: Turmeric Source-Aware & Cross-Dataset Evaluation Protocol
## Phase 4 Protocol Lock

### 1. Scientific Context
In Phase 2 and Phase 3 forensic audits, the dataset labeled **Turmeric Plant Disease (1)** was conclusively proven to be a 100% bit-for-bit duplicate and structural derivative of **Turmeric Plant Disease Dataset Advancing AI (Original)** (all 599 leaf images share identical SHA-256 fingerprints).

Consequently, **Turmeric Plant Disease (1) cannot be used as an independent external test set**. Treating it as such would constitute duplicate-reporting and severe test-set leakage.

However, LeafLens possesses **two genuinely independent turmeric source datasets**:
1. **Source A**: `Image Dataset for Turmeric Plant Leaf Disease Detection (Original)` (644 candidate images)
2. **Source B**: `Turmeric Plant Disease Dataset Advancing AI (Original)` (599 candidate images)

---

### 2. Class Overlap Matrix Between Independent Sources

| Turmeric Class | Present in Source A (Leaf Disease) | Present in Source B (Advancing AI) | Overlap Status |
|----------------|-------------------------------------|------------------------------------|----------------|
| **Healthy** | **213 images** | **197 images** | **SHARED CLASS (410 total)** |
| **Leaf Blotch** | **238 images** | **199 images** | **SHARED CLASS (437 total)** |
| **Dry Leaf** | *Absent (0)* | **203 images** | Source B Exclusive |
| **Leaf Spot** | **193 images** | *Absent (0)* | Source A Exclusive |

> [!IMPORTANT]
> **Strict Evaluation Rule**: A 4-class cross-dataset evaluation across Source A and Source B is mathematically impossible because neither source contains all four classes.
> We must **NOT force a 4-class evaluation** by hallucinating or mislabeling classes.
> Instead, cross-dataset transfer is evaluated exclusively on the **two shared classes** (`Healthy` and `Leaf Blotch`), while unshared classes serve as an **Out-Of-Distribution (OOD) / Anomaly Detection** evaluation.

---

### 3. Formal Source-Held-Out Experiment Protocols

#### Experiment Protocol 1: `TURM_CROSS_B_TO_A`
- **Training Source**: Source B (*Advancing AI Original*, 599 images: Healthy, Leaf Blotch, Dry Leaf)
- **Held-Out Test Source**: Source A (*Turmeric Leaf Disease Original*, 644 images)
- **Shared In-Distribution Classes**: `Healthy` (213 images) and `Leaf Blotch` (238 images) → **451 test images**.
- **OOD / Excluded Class**: `Leaf Spot` (193 images from Source A).
  - *Evaluation Role*: Tests whether the model's uncertainty/rejection mechanism correctly flags `Leaf Spot` as an unfamiliar disease rather than misclassifying it as `Leaf Blotch`.

#### Experiment Protocol 2: `TURM_CROSS_A_TO_B`
- **Training Source**: Source A (*Turmeric Leaf Disease Original*, 644 images: Healthy, Leaf Blotch, Leaf Spot)
- **Held-Out Test Source**: Source B (*Advancing AI Original*, 599 images)
- **Shared In-Distribution Classes**: `Healthy` (197 images) and `Leaf Blotch` (199 images) → **396 test images**.
- **OOD / Excluded Class**: `Dry Leaf` (203 images from Source B).
  - *Evaluation Role*: Tests uncertainty rejection on abiotic stress symptoms not seen during training.

---

### 4. Manifest Location
The machine-readable image assignment list for this protocol is saved at:
👉 [`data/metadata/turmeric_external_protocol.csv`](data/metadata/turmeric_external_protocol.csv)
