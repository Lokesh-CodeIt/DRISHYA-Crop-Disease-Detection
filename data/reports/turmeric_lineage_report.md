# LeafLens: Turmeric Dataset Forensic Lineage & Equivalence Investigation
## Phase 3 Forensic Report

### Objective
To definitively establish whether:
1. **"Turmeric Plant Disease (1)"**
and
2. **"Turmeric Plant Disease Dataset Advancing AI for Agricultural Sustainability"**

represent independent scientific datasets, or whether one is a structural, renamed, or derivative copy of the other.

---

### 1. SHA-256 Bit-for-Bit Identity Matrix

| Class Name in Turmeric (1) | Image Count | Matching Class in Advancing AI (Original) | Exact SHA-256 Matches | Match % |
|----------------------------|-------------|-------------------------------------------|-----------------------|---------|
| `Dry Leaf` | 203 | `Dry Leaf` (203 images) | **203** | **100.0%** |
| `Leaf Blotch` | 199 | `Leaf Blotch` (199 images) | **199** | **100.0%** |
| `Healthy Leaf` | 197 | `Healthy Leaf` (197 images) | **197** | **100.0%** |
| `Rhizome Disease Root` | 182 | `Rhizome Rot` (182 images) | 0 exact, **182 dHash <= 1** | **100.0% (Photographic)** |
| `Rhizome Healthy Root` | 282 | *(None present)* | 0 | 0.0% (Unique) |

---

### 2. Forensic Findings & Detailed Lineage Analysis

#### A. Exact Leaf Duplication (599 of 599 Images)
- All 599 leaf images (`Dry Leaf`: 203, `Leaf Blotch`: 199, `Healthy Leaf`: 197) in **Turmeric Plant Disease (1)** are **100% bit-for-bit SHA-256 identical** to the corresponding files in **Turmeric Plant Disease Dataset Advancing AI (Original)**.
- Every single image filename in Turmeric (1) (e.g., `Dry Leaf00001.JPG`) matches the exact same file in Advancing AI.
- There is **zero independent leaf data** in Turmeric Plant Disease (1).

#### B. Rhizome Disease Label Alteration (182 Images)
- The 182 images labeled `Rhizome Disease Root` in Turmeric (1) are the identical photographs as the 182 images labeled `Rhizome Rot` in Advancing AI.
- In Advancing AI, filenames are `Rhizome Rot00001.JPG` to `Rhizome Rot00182.JPG`.
- In Turmeric (1), filenames are renamed to `Rhizome Disease Root00001.JPG` to `Rhizome Disease Root00182.JPG`.
- A perceptual dHash comparison confirms Hamming distance <= 1 across all 182 pairs (minor re-compression from archive re-saving).
- **Conclusion**: This is a direct folder rename of the same photographic specimens.

#### C. Unique Addition in Turmeric (1) (282 Images)
- Turmeric (1) contains one folder that is absent from Advancing AI: `Rhizome Healthy Root` (282 images).
- These 282 images depict healthy excavated turmeric rhizomes and roots.
- Because LeafLens is a foliar disease diagnosis platform, subterranean rhizomes are outside the model scope.

---

### 3. Conclusion & Curation Decision

> [!CAUTION]
> **Definitive Finding**: "Turmeric Plant Disease (1)" is **NOT an independent dataset**. It is a **renamed and structurally derived clone** of the "Advancing AI" dataset with 282 additional healthy root images appended.
>
> Counting both datasets as separate data sources would constitute fraudulent double-counting of test samples and create extreme cross-dataset data leakage.

### Action Taken in LeafLens Manifests:
1. **Turmeric Plant Disease Dataset Advancing AI (Original)** is retained as the authoritative canonical source.
2. All 599 duplicate leaf records in **Turmeric Plant Disease (1)** are flagged with `duplicate_status = "duplicate"` and excluded from training/validation (`is_candidate_for_model = False`).
3. All rhizome images (both diseased and healthy roots) are excluded (`exclusion_reason = "excluded_plant_part_rhizome"`).
4. Turmeric (1) contributes **0 net images** to the final leaf classifier, fully protecting the project against duplicate contamination.
