# LeafLens: Turmeric Class Mapping & Taxonomy Report
## Phase 3 Dataset Curation

This report documents the formal mapping from raw source dataset classes to the final LeafLens turmeric classifier taxonomy.

### Final 4-Class Leaf Taxonomy:
1. **Healthy**
2. **Leaf Blotch**
3. **Dry Leaf**
4. **Leaf Spot**

> [!IMPORTANT]
> **Strict Non-Merge Mandate**: `Leaf Spot` and `Leaf Blotch` are maintained as two completely separate classes. Botanically and diagnostically, Leaf Blotch (*Taphrina maculans*) produces coalescent dirty-yellow/brown blotches with severe foliar scorch, whereas Leaf Spot (*Colletotrichum curcumae* / *Cercospora curcumae*) forms discrete circular-to-oval spots with distinct grey centres and dark brown margins. Merging them would compromise diagnostic fidelity.

---

### Detailed Class Mapping Table

| Source Dataset | Raw Source Class | Plant Part | Condition Type | Final LeafLens Class | Curation Status | Explicit Agronomic & Forensic Rationale |
|----------------|------------------|------------|----------------|----------------------|-----------------|-----------------------------------------|
| Image Dataset for Turmeric Plant Leaf Disease Detection (Original) | `Healthy_Leaf` | Leaf | healthy | **Healthy** | Candidate | Asymptomatic, normal green foliage. Directly corresponds to Healthy. |
| Image Dataset for Turmeric Plant Leaf Disease Detection (Original) | `Blotch` | Leaf | disease | **Leaf Blotch** | Candidate | Caused by *Taphrina maculans*. High-resolution field photos. |
| Image Dataset for Turmeric Plant Leaf Disease Detection (Original) | `Leaf_Spot` | Leaf | disease | **Leaf Spot** | Candidate | Caused by *Colletotrichum curcumae*. Discrete circular/oval foliar lesions. Kept strictly distinct from Blotch. |
| Image Dataset for Turmeric Plant Leaf Disease Detection (Original) | `Aphids_Disease` | Leaf | pest | *Excluded* | Excluded (`excluded_class_aphids`) | Arthropod pest infestation (*Aphis gossypii* / *Pentalonia nigronervosa*). Out of scope for foliar fungal/stress classifier. |
| Image Dataset for Turmeric Plant Leaf Disease Detection (Augmented) | *All 4 Classes* | Leaf | Various | *Excluded* | Excluded (`author_augmented_prefer_post_split_aug`) | Author-generated pre-augmented files (224x224). Excluded to prevent data leakage; post-split augmentation will be generated deterministically on train fold only. |
| Turmeric Plant Disease Dataset Advancing AI (Original) | `Healthy Leaf` | Leaf | healthy | **Healthy** | Candidate | Normal green turmeric leaves. 100% resolution-uniform (1000x1000). |
| Turmeric Plant Disease Dataset Advancing AI (Original) | `Leaf Blotch` | Leaf | disease | **Leaf Blotch** | Candidate | High-fidelity foliar blotch imagery. |
| Turmeric Plant Disease Dataset Advancing AI (Original) | `Dry Leaf` | Leaf | deficiency_or_stress | **Dry Leaf** | Candidate | Moisture stress, leaf desiccation, or senescence. Critical diagnostic category for field advisory. |
| Turmeric Plant Disease Dataset Advancing AI (Original) | `Rhizome Rot` | Rhizome / Root | disease | *Excluded* | Excluded (`excluded_plant_part_rhizome`) | Subterranean rhizome rot (*Pythium aphanidermatum*). LeafLens mobile/web vision workflow targets above-ground foliar inspection. |
| Turmeric Plant Disease Dataset Advancing AI (Augmented) | *All 4 Classes* | Leaf/Rhizome | Various | *Excluded* | Excluded (`author_augmented_prefer_post_split_aug`) | Author augmentations excluded from candidate split pool. |
| Turmeric Plant Disease (1) | `Dry Leaf` | Leaf | deficiency_or_stress | **Dry Leaf** | Excluded (`duplicate_of_advancing_ai`) | 100% exact bit-for-bit SHA-256 duplicate of Advancing AI Dry Leaf. Excluded to avoid duplicate counting. |
| Turmeric Plant Disease (1) | `Healthy Leaf` | Leaf | healthy | **Healthy** | Excluded (`duplicate_of_advancing_ai`) | 100% exact bit-for-bit SHA-256 duplicate of Advancing AI Healthy Leaf. Excluded to avoid duplicate counting. |
| Turmeric Plant Disease (1) | `Leaf Blotch` | Leaf | disease | **Leaf Blotch** | Excluded (`duplicate_of_advancing_ai`) | 100% exact bit-for-bit SHA-256 duplicate of Advancing AI Leaf Blotch. Excluded to avoid duplicate counting. |
| Turmeric Plant Disease (1) | `Rhizome Disease Root` | Rhizome / Root | disease | *Excluded* | Excluded (`excluded_plant_part_rhizome`) | Rhizome rot duplicate/variant of Advancing AI Rhizome Rot; non-leaf anatomical part. |
| Turmeric Plant Disease (1) | `Rhizome Healthy Root` | Rhizome / Root | healthy | *Excluded* | Excluded (`excluded_plant_part_rhizome`) | Healthy subterranean root/rhizome imagery. Non-leaf anatomical part. |

---

### Candidate Turmeric Image Pool Summary

| Final Class | Source 1: Leaf Disease (Original) | Source 2: Advancing AI (Original) | Total Candidate Images |
|-------------|-----------------------------------|-----------------------------------|------------------------|
| **Healthy** | 213 | 197 | **410** |
| **Leaf Blotch** | 238 | 199 | **437** |
| **Dry Leaf** | 0 | 203 | **203** |
| **Leaf Spot** | 193 | 0 | **193** |
| **TOTAL** | **644** | **599** | **1,243** |

*Overall Class Imbalance Ratio*: 437 / 193 = **2.26×** (Extremely well-balanced dataset for multi-class deep learning).
