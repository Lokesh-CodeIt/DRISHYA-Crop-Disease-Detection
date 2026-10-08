"""
temperature_scaler.py - LeafLens Confidence Calibration & Uncertainty Rejection

Applies learned post-hoc Temperature Scaling to raw output logits:
    p_calibrated = softmax(logits / T)

When the highest calibrated confidence fails to meet the safety threshold (default 0.65),
the prediction is rejected, triggering an uncertainty fallback advising the farmer
to consult local KVK or agricultural extension officers rather than trusting an uncertain prediction.
"""

from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json
import logging
import numpy as np

from ..utils.config import settings

logger = logging.getLogger("LeafLens.TemperatureScaler")


@dataclass
class CalibrationResult:
    calibrated_probs: Optional[np.ndarray]
    raw_probs: np.ndarray
    top_class_idx: int
    raw_confidence: float
    calibrated_confidence: Optional[float]
    is_rejected: bool
    rejection_reason: str = ""
    temperature_applied: Optional[float] = None
    is_active: bool = False


class TemperatureScaler:
    """Performs inference-time temperature scaling and rejection check."""

    def __init__(self, default_threshold: Optional[float] = None):
        self.default_threshold = default_threshold or settings.UNCERTAINTY_REJECTION_THRESHOLD
        self._learned_temperatures: Dict[str, float] = {}
        self._load_calibration_artifacts()

    def _load_calibration_artifacts(self):
        """Loads learned temperature parameters from ml/calibration artifacts."""
        base_dir = settings.BASE_DIR
        calib_dir = base_dir / "ml" / "calibration"

        for crop in ["turmeric", "citrus"]:
            artifact_file = calib_dir / f"{crop}_temperature.json"
            if artifact_file.exists():
                try:
                    with open(artifact_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if "temperature" in data:
                            t = float(data["temperature"])
                            if t > 0:
                                self._learned_temperatures[crop] = t
                                logger.info(f"Loaded learned temperature for '{crop}': T = {t:.6f}")
                except Exception as e:
                    logger.warning(f"Could not load calibration artifact for '{crop}': {e}")

    def reload_artifacts(self):
        """Reloads calibration artifacts from disk."""
        self._load_calibration_artifacts()

    def is_calibration_active(self, crop: Optional[str] = None) -> bool:
        """
        Returns True if calibration is enabled and learned calibration artifacts exist for crop.
        Step C.1 Policy:
        - turmeric: False (calibration inactive for farmer safety)
        - citrus: True (calibration active, T=2.218093)
        - unknown / None: False (calibration inactive by default)
        """
        if crop is None:
            return False
        crop_clean = crop.lower().strip()
        enabled_by_crop = getattr(settings, "CALIBRATION_ENABLED_BY_CROP", {})
        if not enabled_by_crop.get(crop_clean, False):
            return False
        return crop_clean in self._learned_temperatures

    def get_temperature(self, crop: Optional[str] = None) -> float:
        """
        Retrieves the temperature for a crop.
        Prioritizes:
        1. Learned temperature from calibration artifact
        2. Config setting (TURMERIC_TEMPERATURE / CITRUS_TEMPERATURE)
        3. Fallback T = 1.0
        """
        if crop:
            crop_clean = crop.lower().strip()
            if crop_clean in self._learned_temperatures:
                return self._learned_temperatures[crop_clean]
            if crop_clean == "turmeric":
                return getattr(settings, "TURMERIC_TEMPERATURE", 1.0)
            elif crop_clean == "citrus":
                return getattr(settings, "CITRUS_TEMPERATURE", 1.0)
        return 1.0

    @staticmethod
    def softmax(x: np.ndarray) -> np.ndarray:
        """Numerically stable softmax."""
        e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return e_x / np.sum(e_x, axis=-1, keepdims=True)

    def calibrate(
        self,
        logits: np.ndarray,
        crop: Optional[str] = None,
        temperature: Optional[float] = None,
        threshold: Optional[float] = None,
    ) -> CalibrationResult:
        """
        Calibrates logits with scalar temperature T and checks rejection threshold.
        When calibration is active:
          - Applies learned temperature scaling (logits / T)
          - Computes calibrated probabilities
          - Rejection gating evaluates calibrated top-1 confidence against threshold
        When calibration is inactive (e.g. Turmeric or unknown crop):
          - Preserves raw softmax probabilities without logit transformation
          - calibrated_confidence = None, temperature_applied = None, is_active = False
          - Rejection gating evaluates raw top-1 confidence against threshold
        """
        if threshold is None:
            threshold = self.default_threshold

        # Ensure logits is at least 2D
        logits_arr = np.asarray(logits, dtype=np.float32)
        if logits_arr.ndim == 1:
            logits_arr = np.expand_dims(logits_arr, axis=0)

        # Raw probabilities (numerically stable)
        raw_probs = self.softmax(logits_arr)[0]
        top_raw_idx = int(np.argmax(raw_probs))
        top_raw_conf = float(raw_probs[top_raw_idx])

        # Determine activation and temperature
        is_active = False
        t_val: Optional[float] = None

        if temperature is not None:
            t_val = max(float(temperature), 0.01)
            is_active = True
        elif crop is not None and self.is_calibration_active(crop):
            crop_clean = crop.lower().strip()
            t_val = self._learned_temperatures.get(crop_clean, self.get_temperature(crop_clean))
            is_active = True
        else:
            is_active = False
            t_val = None

        if is_active and t_val is not None:
            # Active calibration: logits / T
            calibrated_probs = self.softmax(logits_arr / t_val)[0]
            top_calib_idx = int(np.argmax(calibrated_probs))
            top_calib_conf = float(calibrated_probs[top_calib_idx])

            is_rejected = top_calib_conf < threshold
            rejection_reason = ""
            if is_rejected:
                rejection_reason = (
                    f"Prediction uncertainty high (calibrated confidence {top_calib_conf:.1%} "
                    f"below safety threshold of {threshold:.1%}). Directing to agricultural expert consultation."
                )

            return CalibrationResult(
                calibrated_probs=calibrated_probs,
                raw_probs=raw_probs,
                top_class_idx=top_calib_idx,
                raw_confidence=top_raw_conf,
                calibrated_confidence=top_calib_conf,
                is_rejected=is_rejected,
                rejection_reason=rejection_reason,
                temperature_applied=float(t_val),
                is_active=True,
            )
        else:
            # Inactive calibration: do NOT transform logits, use raw confidence for rejection
            is_rejected = top_raw_conf < threshold
            rejection_reason = ""
            if is_rejected:
                rejection_reason = (
                    f"Prediction uncertainty high (raw confidence {top_raw_conf:.1%} "
                    f"below safety threshold of {threshold:.1%}). Directing to agricultural expert consultation."
                )

            return CalibrationResult(
                calibrated_probs=None,
                raw_probs=raw_probs,
                top_class_idx=top_raw_idx,
                raw_confidence=top_raw_conf,
                calibrated_confidence=None,
                is_rejected=is_rejected,
                rejection_reason=rejection_reason,
                temperature_applied=None,
                is_active=False,
            )


scaler = TemperatureScaler()
