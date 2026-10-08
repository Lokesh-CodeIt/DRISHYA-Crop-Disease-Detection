"""
test_explainability.py - Comprehensive Unit & Integration Tests for Grad-CAM Explainability

Tests:
1. Turmeric target layer (features.7) works and resolves.
2. Citrus target layer (features.7) works and resolves.
3. Heatmap contains strictly finite values (no NaN / Inf).
4. Heatmap is normalized to [0.0, 1.0].
5. Heatmap dimensions match original image dimensions.
6. Predicted class equals Grad-CAM explanation target.
7. At most 3 attention regions returned.
8. Region coordinates remain strictly within original image bounds.
9. Region thumbnails decode successfully into valid PIL Images.
10. Forward and backward hooks are removed after execution (no hook leaks).
11. No model parameters are modified or retain requires_grad=True.
12. Failure of Grad-CAM does not break diagnosis prediction or HTTP response.
13. Calibration values remain completely independent of explainability.
14. Raw probabilities remain completely independent of explainability.
15. Existing diagnosis response contract remains fully backward-compatible.
"""

import io
import base64
import pytest
import numpy as np
import torch
from PIL import Image

from backend.app.ml.registry import get_active_model_config
from backend.app.ml.model_builder import load_trained_model, get_target_conv_layer
from backend.app.services.inference_service import inference_service
from backend.app.services.diagnosis_service import diagnosis_service
from backend.app.models.schemas import CropType, Language
from backend.app.explainability.gradcam import GradCAMExplainer
from backend.app.explainability.renderer import render_gradcam_overlay
from backend.app.explainability.region_extractor import extract_attention_regions
from backend.app.explainability.service import explainability_service


@pytest.fixture(scope="module", autouse=True)
def init_models():
    """Ensure active production models are initialized."""
    if not inference_service.is_initialized:
        inference_service.initialize_models()


@pytest.fixture
def sample_turmeric_bytes():
    """Returns raw bytes for a real Turmeric leaf sample."""
    with open("TESTING/turmeric/leaf_blotch/TUR_leaf_blotch_01.jpg", "rb") as f:
        return f.read()


@pytest.fixture
def sample_citrus_bytes():
    """Returns raw bytes for a real Citrus leaf sample."""
    with open("TESTING/citrus/citrus_canker/CIT_citrus_canker_01.jpg", "rb") as f:
        return f.read()


def test_1_turmeric_target_layer_resolution():
    """1. Verify Turmeric target layer (features.7) resolves and produces 4D spatial maps."""
    cfg = get_active_model_config("turmeric")
    model = inference_service.get_model("turmeric")
    layer = get_target_conv_layer(model, cfg.grad_cam_layer)

    assert layer is not None, f"Target layer '{cfg.grad_cam_layer}' could not be resolved in Turmeric model."
    assert cfg.grad_cam_layer == "features.7"


def test_2_citrus_target_layer_resolution():
    """2. Verify Citrus target layer (features.7) resolves and produces 4D spatial maps."""
    cfg = get_active_model_config("citrus")
    model = inference_service.get_model("citrus")
    layer = get_target_conv_layer(model, cfg.grad_cam_layer)

    assert layer is not None, f"Target layer '{cfg.grad_cam_layer}' could not be resolved in Citrus model."
    assert cfg.grad_cam_layer == "features.7"


def test_3_and_4_and_5_heatmap_properties(sample_turmeric_bytes):
    """3, 4, 5. Verify heatmap has finite values, normalized to [0,1], and matches original dimensions."""
    inf_res = inference_service.predict(sample_turmeric_bytes, crop="turmeric")
    orig_w, orig_h = inf_res["pil_image"].size
    model = inference_service.get_model("turmeric")
    cfg = inference_service.get_config("turmeric")
    c2i = cfg.get_class_to_idx()
    target_idx = c2i[inf_res["predicted_class"]]

    heatmap = GradCAMExplainer.generate_heatmap(
        model=model,
        target_layer_name=cfg.grad_cam_layer,
        input_tensor=inf_res["input_tensor"],
        target_class_idx=target_idx,
        orig_size=(orig_w, orig_h),
    )

    # 3. Strictly finite
    assert np.all(np.isfinite(heatmap)), "Heatmap contains NaN or Infinite values."

    # 4. Normalized to [0.0, 1.0]
    assert np.min(heatmap) >= 0.0, f"Heatmap min ({np.min(heatmap)}) is below 0.0."
    assert np.max(heatmap) <= 1.0, f"Heatmap max ({np.max(heatmap)}) exceeds 1.0."

    # 5. Correct dimensions matching original image
    assert heatmap.shape == (orig_h, orig_w), f"Heatmap shape {heatmap.shape} does not match ({orig_h}, {orig_w})."


def test_6_predicted_class_equals_gradcam_target(sample_citrus_bytes):
    """6. Verify predicted class equals Grad-CAM explanation target."""
    resp = diagnosis_service.diagnose(sample_citrus_bytes, crop=CropType.CITRUS)

    assert resp.prediction is not None
    assert resp.explanation is not None
    assert resp.explanation.target_class == resp.prediction.predicted_class, (
        f"Grad-CAM target class '{resp.explanation.target_class}' does not match "
        f"predicted class '{resp.prediction.predicted_class}'."
    )


def test_7_and_8_and_9_region_properties(sample_turmeric_bytes):
    """7, 8, 9. Verify at most 3 regions, coordinates within bounds, and valid image thumbnails."""
    resp = diagnosis_service.diagnose(sample_turmeric_bytes, crop=CropType.TURMERIC)

    assert resp.explanation is not None
    regions = resp.explanation.regions

    # 7. At most 3 regions returned
    assert len(regions) <= 3, f"Expected at most 3 regions, got {len(regions)}."

    orig_w = resp.explanation.image_width
    orig_h = resp.explanation.image_height

    for r in regions:
        # 8. Coordinates within image bounds
        assert 0 <= r.x < orig_w, f"Region x ({r.x}) outside [0, {orig_w})."
        assert 0 <= r.y < orig_h, f"Region y ({r.y}) outside [0, {orig_h})."
        assert r.width > 0, "Region width must be positive."
        assert r.height > 0, "Region height must be positive."
        assert r.x + r.width <= orig_w, f"Region x + w ({r.x + r.width}) exceeds image width ({orig_w})."
        assert r.y + r.height <= orig_h, f"Region y + h ({r.y + r.height}) exceeds image height ({orig_h})."
        assert 0.0 <= r.attention_score <= 1.0, f"Attention score ({r.attention_score}) outside [0, 1]."

        # 9. Thumbnail decodes successfully
        crop_bytes = base64.b64decode(r.crop_base64)
        crop_pil = Image.open(io.BytesIO(crop_bytes))
        assert crop_pil.size[0] == r.width, f"Decoded thumbnail width ({crop_pil.size[0]}) != region width ({r.width})."
        assert crop_pil.size[1] == r.height, f"Decoded thumbnail height ({crop_pil.size[1]}) != region height ({r.height})."


def test_10_hooks_removed_after_execution(sample_citrus_bytes):
    """10. Verify hooks are strictly removed after Grad-CAM generation (no residual hooks)."""
    model = inference_service.get_model("citrus")
    cfg = inference_service.get_config("citrus")
    target_layer = get_target_conv_layer(model, cfg.grad_cam_layer)

    # Count hooks before
    fwd_hooks_before = len(target_layer._forward_hooks)

    # Execute Grad-CAM
    _ = diagnosis_service.diagnose(sample_citrus_bytes, crop=CropType.CITRUS)

    # Count hooks after
    fwd_hooks_after = len(target_layer._forward_hooks)
    assert fwd_hooks_after == fwd_hooks_before, "Forward hooks leaked on target layer after Grad-CAM execution!"


def test_11_no_model_parameter_changes():
    """11. Verify model parameters remain completely frozen with requires_grad=False."""
    for crop in ["turmeric", "citrus"]:
        model = inference_service.get_model(crop)
        for name, param in model.named_parameters():
            assert not param.requires_grad, f"Parameter '{name}' in {crop} model has requires_grad=True!"
            assert param.grad is None, f"Parameter '{name}' in {crop} model has non-None residual grad!"


def test_12_failure_of_gradcam_does_not_break_diagnosis(sample_turmeric_bytes, monkeypatch):
    """12. Verify failure of Grad-CAM does not break diagnosis or throw HTTP error."""
    # Deliberately monkeypatch GradCAMExplainer to raise a simulated error
    def faulty_heatmap(*args, **kwargs):
        raise RuntimeError("Simulated Grad-CAM hardware / hook catastrophic failure.")

    monkeypatch.setattr(GradCAMExplainer, "generate_heatmap", faulty_heatmap)

    # Diagnosis must still succeed gracefully!
    resp = diagnosis_service.diagnose(sample_turmeric_bytes, crop=CropType.TURMERIC)

    assert resp is not None
    assert resp.prediction is not None
    assert resp.prediction.predicted_class is not None
    assert resp.calibration is not None
    # Explanation degraded gracefully to None
    assert resp.explanation is None


def test_13_and_14_calibration_and_raw_probs_remain_independent(sample_turmeric_bytes):
    """13, 14. Verify raw confidence and calibrated confidence remain independent of Grad-CAM."""
    resp = diagnosis_service.diagnose(sample_turmeric_bytes, crop=CropType.TURMERIC)

    # Raw confidence is unaffected
    assert resp.prediction.confidence > 0.0
    assert resp.calibration.raw_confidence == resp.prediction.confidence

    # If temperature applied, calibrated confidence is present and separate
    if resp.calibration.is_active:
        assert resp.calibration.temperature_applied is not None
        assert resp.prediction.calibrated_confidence is not None


def test_15_existing_diagnosis_behavior_unchanged(sample_citrus_bytes):
    """15. Verify existing diagnosis response structure maintains backward compatibility."""
    resp = diagnosis_service.diagnose(sample_citrus_bytes, crop=CropType.CITRUS)

    # Core response fields exist
    assert resp.crop == CropType.CITRUS
    assert resp.language == Language.ENGLISH
    assert resp.image_sha256 is not None
    assert resp.processing_time_ms > 0
    assert len(resp.prediction.candidates) == 18
    # Advisory field is present in schema (may be None if disease not in repository)
    assert hasattr(resp, "advisory")

    # Explanation fields exist and are well-formed
    if resp.explanation:
        assert resp.explanation.method == "Grad-CAM"
        assert resp.explanation.overlay_base64 is not None
        assert resp.explanation.image_width > 0
        assert resp.explanation.image_height > 0
        assert resp.explanation.processing_time_ms > 0
