"""
test_calibration.py - Unit and Integration Tests for Confidence Calibration

Validates DRISHYA ML Upgrade Step A:
1. Temperature parameter T > 0 strictly
2. Argmax prediction invariance under temperature scaling
3. Calibrated probabilities sum to 1.0
4. 15-bin ECE computation against known analytical values
5. Multiclass Brier score computation against known analytical values
6. Rejection logic at safety threshold (0.65)
7. Scaler graceful fallback behavior when artifacts are absent
8. Calibration artifact JSON schemas
9. Reliability diagram 15-bin structure
10. End-to-end /diagnose endpoint integration with calibrated confidence
11. Prediction invariance: accuracy and Macro F1 unchanged before and after calibration
"""

import io
import json
from pathlib import Path
import pytest
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.calibration.temperature_scaler import TemperatureScaler, scaler
from backend.app.services.inference_service import inference_service
from backend.app.utils.config import settings
from ml.scripts.calibrate import (
    compute_ece_and_bins,
    compute_brier_score,
    evaluate_metrics,
)

PROJECT_ROOT = settings.BASE_DIR
CALIBRATION_DIR = PROJECT_ROOT / "ml" / "calibration"
CACHE_DIR = CALIBRATION_DIR / "cache"


@pytest.fixture(scope="module", autouse=True)
def init_models():
    """Ensure models are initialized before running inference tests."""
    inference_service.initialize_models()
    scaler.reload_artifacts()


def create_sample_leaf_bytes(size=(300, 300), color=(40, 160, 40)) -> bytes:
    """Creates synthetic leaf image bytes for testing."""
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ===========================================================================
# 1. Temperature Parameter Tests
# ===========================================================================
def test_temperature_parameter_positive():
    """Verifies that learned temperatures for calibrated crops are strictly positive."""
    turm_t = scaler.get_temperature("turmeric")
    assert turm_t > 0.0, f"Turmeric temperature must be > 0, got {turm_t}"
    assert np.isfinite(turm_t)

    # If citrus is calibrated, check citrus too
    citrus_json = CALIBRATION_DIR / "citrus_temperature.json"
    if citrus_json.exists():
        citrus_t = scaler.get_temperature("citrus")
        assert citrus_t > 0.0, f"Citrus temperature must be > 0, got {citrus_t}"
        assert np.isfinite(citrus_t)


# ===========================================================================
# 2. Argmax Invariance Tests
# ===========================================================================
def test_calibration_preserves_argmax():
    """
    Mathematical property: Dividing by scalar T > 0 preserves the ordering
    of logits. Therefore, argmax(z) == argmax(z / T) for all z and T > 0.
    """
    np.random.seed(42)
    # Generate 100 random logit vectors across 18 classes
    logits = np.random.randn(100, 18).astype(np.float32)

    temperatures_to_test = [0.05, 0.10, 0.5, 1.0, 1.25, 2.0, 5.0, 10.0]
    raw_argmax = np.argmax(logits, axis=1)

    for T in temperatures_to_test:
        scaled_argmax = np.argmax(logits / T, axis=1)
        assert np.array_equal(raw_argmax, scaled_argmax), f"Argmax changed for T={T}!"


# ===========================================================================
# 3. Probability Normalization Tests
# ===========================================================================
def test_calibrated_probabilities_sum_to_one():
    """Verifies calibrated probabilities are valid distributions summing to 1.0."""
    np.random.seed(123)
    logits = np.random.randn(50, 4).astype(np.float32)

    for T in [0.1, 0.5, 1.0, 1.8, 3.0]:
        res = scaler.calibrate(logits, temperature=T)
        assert np.isclose(np.sum(res.calibrated_probs), 1.0, atol=1e-5)
        assert np.all(res.calibrated_probs >= 0.0)
        assert np.all(res.calibrated_probs <= 1.0)


# ===========================================================================
# 4. Known-Value ECE Computation Tests
# ===========================================================================
def test_ece_computation_known_values():
    """
    Verifies 15-bin ECE against analytically solvable test cases:
    Case A: Perfect calibration (predictions 100% accurate, confidence 1.0) -> ECE = 0.0
    Case B: Overconfident uncalibrated (predictions 50% accurate, confidence 1.0) -> ECE = 0.5
    """
    # Case A: Perfect calibration
    probs_perfect = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])
    labels_perfect = np.array([0, 0, 1, 1])
    ece_a, _, _ = compute_ece_and_bins(probs_perfect, labels_perfect, n_bins=15)
    assert np.isclose(ece_a, 0.0, atol=1e-5), f"Expected 0.0, got {ece_a}"

    # Case B: 50% accurate, but 100% confident
    # 4 samples: 2 correct, 2 incorrect. All have max prob = 1.0 (bin 14: [0.9333, 1.0])
    probs_overconf = np.array([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [1.0, 0.0]])
    labels_overconf = np.array([0, 0, 1, 1])  # First 2 correct, last 2 wrong
    ece_b, _, _ = compute_ece_and_bins(probs_overconf, labels_overconf, n_bins=15)
    # Bin accuracy = 2/4 = 0.5, bin confidence = 1.0. Gap = |0.5 - 1.0| = 0.5.
    assert np.isclose(ece_b, 0.5, atol=1e-5), f"Expected 0.5, got {ece_b}"


# ===========================================================================
# 5. Known-Value Multiclass Brier Score Tests
# ===========================================================================
def test_brier_score_computation():
    """
    Verifies multiclass Brier score against manual calculation:
    3 samples, 2 classes:
    p1 = [0.8, 0.2], y1 = 0 -> (0.8-1)^2 + (0.2-0)^2 = 0.04 + 0.04 = 0.08
    p2 = [0.6, 0.4], y2 = 0 -> (0.6-1)^2 + (0.4-0)^2 = 0.16 + 0.16 = 0.32
    p3 = [0.1, 0.9], y3 = 1 -> (0.1-0)^2 + (0.9-1)^2 = 0.01 + 0.01 = 0.02
    Mean = (0.08 + 0.32 + 0.02) / 3 = 0.42 / 3 = 0.14
    """
    probs = np.array([[0.8, 0.2], [0.6, 0.4], [0.1, 0.9]])
    labels = np.array([0, 0, 1])
    brier = compute_brier_score(probs, labels, num_classes=2)
    assert np.isclose(brier, 0.14, atol=1e-5), f"Expected 0.14, got {brier}"


# ===========================================================================
# 6. Rejection Logic Tests
# ===========================================================================
def test_rejection_logic_threshold():
    """Verifies rejection trigger below safety threshold 0.65 for both active and inactive calibration."""
    threshold = 0.65

    # Case A1: High uncertainty with active calibration (Citrus)
    uncertain_logits = np.array([[0.0, 0.0, 0.0, 0.0]], dtype=np.float32)
    res_uncertain_citrus = scaler.calibrate(uncertain_logits, crop="citrus", threshold=threshold)
    assert res_uncertain_citrus.is_active is True
    assert res_uncertain_citrus.calibrated_confidence < threshold
    assert res_uncertain_citrus.is_rejected is True
    assert "uncertainty high" in res_uncertain_citrus.rejection_reason.lower()
    assert "consultation" in res_uncertain_citrus.rejection_reason.lower()

    # Case A2: High uncertainty with inactive calibration (Turmeric)
    res_uncertain_turm = scaler.calibrate(uncertain_logits, crop="turmeric", threshold=threshold)
    assert res_uncertain_turm.is_active is False
    assert res_uncertain_turm.calibrated_confidence is None
    assert res_uncertain_turm.raw_confidence < threshold
    assert res_uncertain_turm.is_rejected is True
    assert "uncertainty high" in res_uncertain_turm.rejection_reason.lower()

    # Case B: High confidence prediction (dominant logit -> prob ~ 0.999)
    confident_logits = np.array([[10.0, 0.0, 0.0, 0.0]], dtype=np.float32)
    res_confident = scaler.calibrate(confident_logits, crop="citrus", threshold=threshold)
    assert res_confident.calibrated_confidence >= threshold
    assert res_confident.is_rejected is False
    assert res_confident.rejection_reason == ""


# ===========================================================================
# 7. Scaler Fallback Behavior Tests
# ===========================================================================
def test_scaler_fallback_behavior():
    """Verifies graceful fallback to T=1.0 and is_active=False on unknown crops."""
    unknown_crop = "non_existent_crop"
    temp = scaler.get_temperature(unknown_crop)
    assert temp == 1.0
    assert scaler.is_calibration_active(unknown_crop) is False

    logits = np.array([[2.0, 1.0]], dtype=np.float32)
    res = scaler.calibrate(logits, crop=unknown_crop)
    assert res.temperature_applied is None
    assert res.is_active is False
    assert res.calibrated_confidence is None
    assert res.calibrated_probs is None


# ===========================================================================
# 8. Calibration Artifact Schema Tests
# ===========================================================================
def test_artifact_schema_validity():
    """Verifies JSON artifacts exist, parse, and conform to the expected schema."""
    turm_json = CALIBRATION_DIR / "turmeric_temperature.json"
    assert turm_json.exists(), "turmeric_temperature.json artifact missing!"

    with open(turm_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["crop"] == "turmeric"
    assert data["model_architecture"] == "convnext_tiny"
    assert data["seed"] == 42
    assert data["num_classes"] == 4
    assert data["temperature"] > 0
    assert "val_metrics" in data
    assert "test_metrics" in data
    assert "ece" in data["val_metrics"]["post"]
    assert "nll" in data["val_metrics"]["post"]
    assert "brier_score" in data["val_metrics"]["post"]

    # Check calibration_report.json
    report_json = CALIBRATION_DIR / "calibration_report.json"
    assert report_json.exists(), "calibration_report.json missing!"
    with open(report_json, "r", encoding="utf-8") as f:
        rep = json.load(f)
    assert "crops" in rep
    assert "turmeric" in rep["crops"]


# ===========================================================================
# 9. Reliability Diagram Structure Tests
# ===========================================================================
def test_reliability_diagram_bins():
    """Verifies reliability data contains 15 equal-width bins spanning [0, 1]."""
    rel_json = CALIBRATION_DIR / "reliability_data.json"
    assert rel_json.exists(), "reliability_data.json missing!"

    with open(rel_json, "r", encoding="utf-8") as f:
        rel = json.load(f)

    assert "crops" in rel
    assert "turmeric" in rel["crops"]
    turm_rel = rel["crops"]["turmeric"]

    val_bins = turm_rel["validation"]["calibrated_bins"]
    assert len(val_bins) == 15

    for b in val_bins:
        assert 0.0 <= b["bin_lower"] <= 1.0
        assert 0.0 <= b["bin_upper"] <= 1.0
        assert b["bin_lower"] < b["bin_upper"]
        assert b["sample_count"] >= 0
        if b["sample_count"] > 0:
            assert 0.0 <= b["bin_confidence"] <= 1.0
            assert 0.0 <= b["bin_accuracy"] <= 1.0


# ===========================================================================
# 10. End-to-End /diagnose API Integration Tests & Step C.1 Policy Tests
# ===========================================================================
def test_end_to_end_diagnose_calibration_citrus():
    """Verifies that Citrus diagnosis has ACTIVE calibration with T=2.218093."""
    scaler.reload_artifacts()
    client = TestClient(app)
    sample_bytes = create_sample_leaf_bytes()

    response = client.post(
        "/api/v1/diagnose",
        files={"file": ("leaf.jpg", sample_bytes, "image/jpeg")},
        data={"crop": "citrus", "language": "en"},
    )
    assert response.status_code == 200
    data = response.json()

    # Prediction fields
    assert data["prediction"]["confidence"] > 0.0
    assert data["prediction"]["calibrated_confidence"] is not None
    assert data["prediction"]["calibrated_confidence"] > 0.0
    assert isinstance(data["prediction"]["is_rejected"], bool)

    # CalibrationInfo fields
    calib = data["calibration"]
    assert calib["is_active"] is True
    assert calib["temperature_applied"] == 2.218093
    assert calib["calibrated_confidence"] is not None
    assert calib["raw_confidence"] == data["prediction"]["confidence"]

    # Candidates breakdown: populated with calibrated_probability
    candidates = data["prediction"]["candidates"]
    assert len(candidates) == 18
    for c in candidates:
        assert c["calibrated_probability"] is not None
        assert 0.0 <= c["calibrated_probability"] <= 1.0


def test_end_to_end_diagnose_calibration_turmeric():
    """Verifies that Turmeric diagnosis has INACTIVE calibration per Step C.1 safety policy."""
    scaler.reload_artifacts()
    client = TestClient(app)
    sample_bytes = create_sample_leaf_bytes()

    response = client.post(
        "/api/v1/diagnose",
        files={"file": ("leaf.jpg", sample_bytes, "image/jpeg")},
        data={"crop": "turmeric", "language": "en"},
    )
    assert response.status_code == 200
    data = response.json()

    # Prediction fields: calibrated_confidence is None
    assert data["prediction"]["confidence"] > 0.0
    assert data["prediction"]["calibrated_confidence"] is None
    assert isinstance(data["prediction"]["is_rejected"], bool)

    # CalibrationInfo fields: is_active is False, temperature_applied is None
    calib = data["calibration"]
    assert calib["is_active"] is False
    assert calib["temperature_applied"] is None
    assert calib["calibrated_confidence"] is None
    assert calib["raw_confidence"] == data["prediction"]["confidence"]

    # Candidates breakdown: calibrated_probability is None, raw_probability is present
    candidates = data["prediction"]["candidates"]
    assert len(candidates) == 4
    for c in candidates:
        assert c["raw_probability"] is not None
        assert c["calibrated_probability"] is None


def test_step_c1_crop_specific_policy():
    """Step C.1 Policy Unit Test: Turmeric inactive, Citrus active, Unknown inactive."""
    # A. Turmeric:
    assert scaler.is_calibration_active("turmeric") is False
    turm_logits = np.array([[2.5, 1.0, 0.5, 0.1]], dtype=np.float32)
    turm_res = scaler.calibrate(turm_logits, crop="turmeric")
    assert turm_res.is_active is False
    assert turm_res.calibrated_confidence is None
    assert turm_res.temperature_applied is None
    assert turm_res.calibrated_probs is None
    assert np.isclose(turm_res.raw_confidence, scaler.softmax(turm_logits)[0, 0], atol=1e-5)

    # B. Citrus:
    assert scaler.is_calibration_active("citrus") is True
    citrus_logits = np.array([[3.0, 1.0, 0.2]], dtype=np.float32)
    citrus_res = scaler.calibrate(citrus_logits, crop="citrus")
    assert citrus_res.is_active is True
    assert citrus_res.temperature_applied == 2.218093
    assert citrus_res.calibrated_confidence is not None
    expected_calib_p = scaler.softmax(citrus_logits / 2.218093)[0, 0]
    assert np.isclose(citrus_res.calibrated_confidence, expected_calib_p, atol=1e-5)

    # C. Unknown crop:
    assert scaler.is_calibration_active("unknown_crop") is False
    unk_res = scaler.calibrate(turm_logits, crop="unknown_crop")
    assert unk_res.is_active is False
    assert unk_res.temperature_applied is None
    assert unk_res.calibrated_confidence is None


# ===========================================================================
# 11. Prediction Invariance: Accuracy and F1 Invariant
# ===========================================================================
def test_prediction_invariance_accuracy_f1():
    """Verifies that accuracy and Macro F1 do NOT change under temperature scaling."""
    val_cache = CACHE_DIR / "turmeric_val_logits.npz"
    test_cache = CACHE_DIR / "turmeric_test_logits.npz"

    assert val_cache.exists(), "Turmeric val logits cache missing!"
    assert test_cache.exists(), "Turmeric test logits cache missing!"

    val_data = np.load(val_cache)
    test_data = np.load(test_cache)

    T = scaler.get_temperature("turmeric")

    for split_data, name in [(val_data, "Val"), (test_data, "Test")]:
        logits = split_data["logits"]
        labels = split_data["labels"]

        m_raw = evaluate_metrics(logits, labels, temperature=1.0)
        m_cal = evaluate_metrics(logits, labels, temperature=T)

        assert m_raw["accuracy"] == m_cal["accuracy"], f"{name} accuracy differed!"
        assert m_raw["macro_f1"] == m_cal["macro_f1"], f"{name} Macro F1 differed!"
        assert np.array_equal(
            np.argmax(logits, axis=1), np.argmax(logits / T, axis=1)
        ), f"{name} predictions differed!"
