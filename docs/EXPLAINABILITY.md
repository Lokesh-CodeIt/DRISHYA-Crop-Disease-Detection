# DRISHYA — Explainability Documentation

## Overview

DRISHYA uses **Grad-CAM** (Gradient-weighted Class Activation Mapping) to generate visual explanations for model predictions. The system produces a heatmap overlay on the input image and extracts real attention-region crops highlighting the image areas most influential to the prediction.

---

## Method: Grad-CAM

Grad-CAM computes the gradient of the predicted class logit with respect to the activations of a target convolutional layer. These gradients are global-average-pooled to produce weights, which are then used to create a weighted sum of the feature maps. The result is a coarse heatmap that highlights which image regions the model attended to.

**Reference:** Selvaraju et al. (2017). "Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization."

---

## Implementation

Implemented in:
- `backend/app/explainability/gradcam.py` — Hook registration and gradient computation
- `backend/app/explainability/gradcam_service.py` — Service orchestration
- `backend/app/explainability/region_extractor.py` — Region bounding box extraction
- `backend/app/explainability/renderer.py` — Heatmap-to-image compositing

---

## Target Layer

**Target layer: `features.7`**

This is the final high-level feature block in both ConvNeXt-Tiny and EfficientNetV2-S architectures, providing the highest-level spatial feature representations before the classification head.

Both models use `features.7` as the Grad-CAM target layer, validated across all 22 supported classes.

---

## Generation Process

1. Forward pass is run with gradients enabled
2. The logit for the **predicted class** is used as the scalar for backward pass
3. Gradients with respect to `features.7` activations are captured via backward hooks
4. Gradient channels are global-average-pooled to produce per-channel weights
5. Weighted sum of feature maps is computed and ReLU applied
6. Heatmap is bilinearly upsampled to match the input image resolution
7. Heatmap is normalized to [0, 1] range
8. Jet colormap applied and alpha-composited with the input image

---

## Region Extraction

After heatmap generation, high-activation regions are extracted:

1. Heatmap thresholded at 50th percentile activation
2. Connected components computed using OpenCV
3. Non-maximum suppression applied to remove overlapping bounding boxes
4. Top regions returned with:
   - Bounding box `(x, y, width, height)`
   - Activation score (percentage of heatmap mass in region)
5. Region crops are extracted from the **original input image** (not the heatmap)

---

## Model Safety During Grad-CAM

- **Model parameters are frozen** during Grad-CAM generation (gradients not applied back)
- **Backward hooks are removed** after heatmap generation to prevent memory leaks
- Calibration and raw probability values remain independent of Grad-CAM computation
- Failure of Grad-CAM (e.g., layer resolution mismatch) does not break the diagnosis response — the overlay is simply omitted

---

## 22-Class Grad-CAM Validation

All 22 supported classes were validated to produce valid Grad-CAM overlays using representative test images:

- 4 turmeric classes (Healthy, Dry Leaf, Leaf Blotch, Leaf Spot)
- 18 citrus classes (all disease/pest/healthy categories)

Validation results documented in:
- `docs/explainability_22_class_validation.md` (summary report)
- `docs/explainability_22_class_validation.csv` (per-class results)

---

## Limitations

- Grad-CAM produces **coarse spatial heatmaps** — resolution is limited by the spatial dimensions of `features.7`, not the full input resolution
- The heatmap highlights correlations learned by the model, **not proven causal disease regions**
- Quantitative lesion localization metrics (IoU, pixel-level F1) are **not claimed**
- For small or uniformly distributed lesions, Grad-CAM may highlight large background areas
- The target layer was chosen empirically; different layers may produce different heatmap characteristics

---

## Scientific Caveat

Grad-CAM is **supporting visual evidence**, not proof of biological causation. The heatmap indicates what information the model used to make its prediction, but this does not guarantee that the highlighted region corresponds to the disease lesion as a pathologist would define it.

Users should interpret Grad-CAM overlays as one signal among many when making field decisions, not as automated lesion identification.
