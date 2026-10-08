# DRISHYA — Calibration Documentation

## Overview

DRISHYA uses **Temperature Scaling** (post-hoc calibration) to align model confidence with true prediction accuracy. Calibration is applied **crop-specifically** based on empirical validation behavior.

---

## What is Temperature Scaling?

Temperature Scaling divides raw model logits by a scalar `T` before applying softmax:

```
calibrated_probability = softmax(logits / T)
```

- `T > 1` → softer (lower confidence) probabilities → reduces overconfidence
- `T < 1` → sharper (higher confidence) probabilities → can increase overconfidence
- `T = 1` → no change from raw softmax

The temperature `T` is fitted on the **validation split** (not the test set) by minimizing Expected Calibration Error (ECE).

---

## Crop-Specific Calibration Policy

### Turmeric — Calibration **INACTIVE**

| Property | Value |
|---|---|
| Fitted Temperature | T = 0.101698 |
| Applied to inference | ❌ No |
| Displayed confidence | Raw softmax |

**Reason calibration is inactive:**

The Turmeric validation split achieved **zero classification errors**. Temperature Scaling fits the calibration temperature by minimizing ECE on the validation logits, but when the model already classifies every validation sample correctly, the optimizer drives `T` toward zero to further sharpen already-correct distributions. The resulting `T = 0.101698` would produce pathologically overconfident probabilities (values near 100%) that are less informative and potentially more misleading than the already-high raw softmax output.

**Decision:** Raw softmax confidence is used for Turmeric inference. The calibration artifact (`ml/calibration/turmeric_temperature.json`) is retained for reproducibility.

---

### Citrus — Calibration **ACTIVE**

| Property | Value |
|---|---|
| Fitted Temperature | T = 2.218093 |
| Applied to inference | ✅ Yes |
| Displayed confidence | Calibrated (Temperature-Scaled) |

**ECE Results (Citrus):**

| Split | Before Calibration | After Calibration |
|---|---|---|
| Validation | 0.062936 | **0.032162** |
| Test | 0.058998 | **0.026995** |

Calibration reduces Citrus ECE by approximately 49% on validation and 54% on test, demonstrating that the calibrated confidence is more reliably aligned with actual prediction accuracy.

---

## Uncertainty Rejection

Both models share a common confidence threshold for uncertainty rejection:

**Threshold: 0.65**

| Condition | Action |
|---|---|
| Calibrated (or raw for Turmeric) confidence ≥ 0.65 | Prediction accepted and displayed |
| Calibrated (or raw for Turmeric) confidence < 0.65 | Prediction **rejected** — expert confirmation messaging shown |

Rejected predictions still display the Grad-CAM overlay (where available) and the rejection reason. They do not display condition knowledge for the tentative class.

---

## Calibration Artifacts

| File | Description |
|---|---|
| `ml/calibration/turmeric_temperature.json` | Fitted T for Turmeric (inactive) |
| `ml/calibration/citrus_temperature.json` | Fitted T for Citrus (active) |
| `ml/calibration/calibration_report.json` | Full calibration report with ECE metrics |
| `ml/calibration/reliability_data.json` | Per-bin reliability diagram data |
| `ml/calibration/cache/*.npz` | Cached logits used for calibration fitting |

---

## Calibration Implementation

Implemented in `backend/app/calibration/temperature_scaler.py`.

The `CropSpecificTemperatureScaler` class:
1. Loads temperature values from the calibration artifact JSONs on startup
2. Checks the crop-specific activation flag (from `backend/app/utils/config.py`)
3. For active crops: applies `logits / T` before softmax
4. For inactive crops: passes raw logits unchanged

The crop-specific activation flags in `config.py`:
```python
CALIBRATION_ENABLED_BY_CROP = {
    "turmeric": False,
    "citrus": True,
}
```

---

## Calibration Fitting Script

Temperature Scaling was fitted using `ml/scripts/calibrate.py`.

The script:
1. Loads pre-computed logit caches (`.npz`) from `ml/calibration/cache/`
2. Optimizes `T` to minimize ECE on the validation logits
3. Evaluates on the test logits
4. Writes temperature and ECE results to artifact files
