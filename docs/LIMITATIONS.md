# DRISHYA — Limitations

This document provides an honest account of all known scientific, engineering, and operational limitations of the DRISHYA research prototype.

---

## 1. Single-Seed Results Only

Only **Seed 42** has been trained and evaluated. No multi-seed experiments were conducted.

This means:
- No mean ± standard deviation accuracy/F1 statistics are available
- Variance across random seeds is unknown
- Results may differ if training is repeated with a different random seed

---

## 2. Turmeric Cross-Dataset Evaluation Not Available

A valid **source-isolated cross-dataset experiment** was not performed for the current Turmeric model.

The Turmeric model was trained on a **combined pool** from multiple dataset sources, making it impossible to cleanly evaluate on one dataset "held out" from training without re-engineering the entire dataset pipeline.

This is a known limitation. Quantitative generalization claims for Turmeric beyond the internal test set are not made.

---

## 3. Citrus Domain Shift

The Citrus model shows significant performance degradation on external data:

| Set | Accuracy | Macro F1 |
|---|---|---|
| Internal test | 92.73% | 0.8863 |
| External (held-out) | 66.01% | 0.4892 |

**Macro F1 drop: 44.8%**

This demonstrates that the model's internal test performance does not generalize reliably to external field conditions. Users should not assume internal test accuracy reflects expected field performance.

---

## 4. Grad-CAM Quantitative Localization Not Available

Grad-CAM overlays provide qualitative visual attention maps. **Quantitative lesion localization metrics** (e.g., IoU between heatmap and ground-truth lesion mask, pixel-level F1) are not available.

Reasons:
- Ground-truth pixel-level lesion annotations are not available for the training/test datasets
- Grad-CAM resolution is limited by the spatial dimensions of `features.7`

The system documents validated coverage (22/22 classes produce valid overlays) but does not claim lesion localization accuracy.

---

## 5. Decision Support, Not Diagnosis

DRISHYA outputs are **decision support** — they are not confirmed disease diagnoses.

The system:
- Does not replace a qualified plant pathologist, agronomist, or agricultural extension officer
- Cannot account for mixed infections, environmental stress, or conditions not in the training data
- Cannot assess disease severity quantitatively
- Cannot observe the full plant context (roots, stems, fruit, environmental conditions)

---

## 6. Confidence ≠ Biological Certainty

Model confidence reflects the model's internal certainty given its training distribution. It does **not** measure:
- Probability that the prediction is biologically correct in the field
- Risk level of the disease
- Urgency of treatment

A high-confidence incorrect prediction is possible, particularly for:
- Novel disease strains or phenotypes
- Images with unusual lighting, background, or composition
- Conditions at symptom onset that appear ambiguous

---

## 7. Class Coverage

| Crop | Classes Supported |
|---|---|
| Turmeric | 4 (Healthy, Dry Leaf, Leaf Blotch, Leaf Spot) |
| Citrus | 18 |

The system cannot recognize:
- Diseases not in the training data
- Crops other than Turmeric and Citrus
- Mixed infections
- Pest damage not represented in training classes

---

## 8. Image Quality Sensitivity

Model performance degrades on:
- Blurry images (low Laplacian sharpness)
- Low-light or overexposed images
- Heavy background clutter
- Partial leaf views
- Multiple leaves per image
- Images taken at extreme angles

The TESTING/edge_cases/ folder documents known failure-prone image conditions.

---

## 9. Dataset Geographic Diversity

Training datasets originate from publicly available Kaggle repositories, which may not represent the geographic, seasonal, and environmental diversity of Indian agricultural conditions.

Field images from diverse Indian farming contexts were not included in training, which likely contributes to the observed Citrus domain shift.

---

## 10. Calibration Limitation (Turmeric)

Temperature Scaling calibration is inactive for Turmeric due to a pathological fitting scenario (zero-error validation split). Raw softmax confidence is used instead, which may be overconfident for borderline cases.

---

## 11. No Severity Estimation

DRISHYA classifies conditions but does not estimate disease severity (e.g., mild / moderate / severe / critical). Severity assessment is not available in the current implementation.

---

## 12. No Dynamic Treatment Generation

Treatment guidance is entirely deterministic and source-backed. No dynamic pesticide recommendations, dosage calculations, or application scheduling is generated. This is intentional for safety — but it also means guidance cannot adapt to local agronomic conditions.

---

## Summary Table

| Limitation | Impact | Status |
|---|---|---|
| Single seed only | No variance estimate | Known |
| No Turmeric cross-dataset eval | No external generalization data | Known |
| Citrus domain shift (44.8% F1 drop) | Reduced field reliability | Documented |
| No Grad-CAM quantitative metrics | No lesion localization accuracy | Known |
| Decision support, not diagnosis | Requires expert verification | By design |
| 4 turmeric classes only | Cannot detect all conditions | Known |
| No severity estimation | Cannot triage urgency | Future scope |
| Image quality sensitivity | Failure on edge case images | Known |
| Limited geographic diversity | May not generalize to all regions | Known |
