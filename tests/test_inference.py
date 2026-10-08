"""
test_inference.py - Unit and Integration Tests for LeafLens Unified Inference Layer

Validates:
1. Turmeric (ConvNeXt-Tiny) and Citrus (EfficientNetV2-S) model loading
2. Evaluation mode and gradient disabling
3. Class counts and exact class mappings
4. Crop-aware input dimensions (224 vs 384)
5. Synthetic image inference forward pass
6. Softmax probability normalization (sum ~ 1.0)
7. End-to-end /diagnose endpoint integration
"""

import io
import pytest
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ml.registry import get_active_model_config, get_registered_seeds, MODEL_REGISTRY
from backend.app.services.inference_service import inference_service
from backend.app.preprocessing.image_pipeline import preprocess_image_bytes, get_crop_target_size


def create_sample_leaf_bytes(size=(400, 400), color=(34, 139, 34)) -> bytes:
    """Generates synthetic RGB leaf photograph bytes for smoke testing."""
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture(scope="module", autouse=True)
def init_models():
    """Ensure models are initialized before running inference tests."""
    inference_service.initialize_models()


# ===========================================================================
# 1. Registry & Policy Tests
# ===========================================================================
def test_turmeric_seed_policy():
    """Verifies Seeds 42, 123, and 7 are registered, but only Seed 42 is active."""
    turm_seeds = get_registered_seeds("turmeric")
    assert set(turm_seeds) == {42, 123, 7}

    cfg_42 = MODEL_REGISTRY["turmeric"][42]
    cfg_123 = MODEL_REGISTRY["turmeric"][123]
    cfg_7 = MODEL_REGISTRY["turmeric"][7]

    assert cfg_42.is_active is True
    assert cfg_42.status == "active"

    assert cfg_123.is_active is False
    assert cfg_123.status == "standby_for_ensemble"

    assert cfg_7.is_active is False
    assert cfg_7.status == "standby_for_ensemble"


def test_citrus_seed_policy():
    """Verifies Citrus has only Seed 42 registered and active."""
    citrus_seeds = get_registered_seeds("citrus")
    assert citrus_seeds == [42]

    cfg_42 = get_active_model_config("citrus")
    assert cfg_42.is_active is True
    assert cfg_42.status == "active"


# ===========================================================================
# 2. Model Loading & Architecture Tests
# ===========================================================================
def test_models_loaded_and_eval_mode():
    """Verifies active models are loaded and in eval mode with no gradients."""
    assert inference_service.is_model_available("turmeric") is True
    assert inference_service.is_model_available("citrus") is True

    turm_model = inference_service.get_model("turmeric")
    citrus_model = inference_service.get_model("citrus")

    assert turm_model.training is False
    assert citrus_model.training is False

    # Check requires_grad is False for all parameters
    for p in turm_model.parameters():
        assert p.requires_grad is False
    for p in citrus_model.parameters():
        assert p.requires_grad is False


def test_turmeric_architecture_and_classes():
    """Verifies Turmeric architecture, class count (4), and exact mapping."""
    cfg = get_active_model_config("turmeric")
    assert cfg.architecture == "convnext_tiny"
    assert cfg.img_size == 224
    assert cfg.num_classes == 4

    classes = inference_service.get_classes("turmeric")
    assert len(classes) == 4
    assert classes == ["Dry Leaf", "Healthy", "Leaf Blotch", "Leaf Spot"]

    mapping = cfg.get_class_to_idx()
    assert mapping == {
        "Dry Leaf": 0,
        "Healthy": 1,
        "Leaf Blotch": 2,
        "Leaf Spot": 3,
    }


def test_citrus_architecture_and_classes():
    """Verifies Citrus architecture, class count (18), and exact mapping."""
    cfg = get_active_model_config("citrus")
    assert cfg.architecture == "efficientnet_v2_s"
    assert cfg.img_size == 384
    assert cfg.num_classes == 18

    classes = inference_service.get_classes("citrus")
    assert len(classes) == 18
    assert classes[0] == "Algal_Leaf_Spot"
    assert classes[-1] == "Yellow_Spot"

    mapping = cfg.get_class_to_idx()
    assert len(mapping) == 18
    assert mapping["Healthy"] == 12
    assert mapping["Citrus Canker"] == 4


# ===========================================================================
# 3. Crop-Aware Preprocessing Tests
# ===========================================================================
def test_crop_aware_preprocessing_dimensions():
    """Verifies crop parameter automatically selects correct target dimensions."""
    sample_bytes = create_sample_leaf_bytes(size=(500, 500))

    assert get_crop_target_size("turmeric") == (224, 224)
    assert get_crop_target_size("citrus") == (384, 384)

    t_tensor, _ = preprocess_image_bytes(sample_bytes, crop="turmeric")
    assert t_tensor.shape == (1, 3, 224, 224)

    c_tensor, _ = preprocess_image_bytes(sample_bytes, crop="citrus")
    assert c_tensor.shape == (1, 3, 384, 384)


# ===========================================================================
# 4. End-to-End Inference Smoke Tests
# ===========================================================================
def test_turmeric_predict_smoke():
    """Executes predict() on Turmeric model with valid leaf sample."""
    sample_bytes = create_sample_leaf_bytes()
    res = inference_service.predict(sample_bytes, crop="turmeric")

    assert res["crop"] == "turmeric"
    assert res["model_name"] == "convnext_tiny"
    assert res["seed"] == 42
    assert res["img_size"] == 224
    assert res["num_classes"] == 4
    assert res["predicted_class"] in ["Dry Leaf", "Healthy", "Leaf Blotch", "Leaf Spot"]

    probs = res["probabilities"]
    assert len(probs) == 4
    assert np.isclose(sum(probs), 1.0, atol=1e-4)

    # Check candidates
    candidates = res["candidates"]
    assert len(candidates) == 4
    assert candidates[0]["class_name"] == res["predicted_class"]
    assert np.isclose(candidates[0]["probability"], res["confidence"])


def test_citrus_predict_smoke():
    """Executes predict() on Citrus model with valid leaf sample."""
    sample_bytes = create_sample_leaf_bytes()
    res = inference_service.predict(sample_bytes, crop="citrus")

    assert res["crop"] == "citrus"
    assert res["model_name"] == "efficientnet_v2_s"
    assert res["seed"] == 42
    assert res["img_size"] == 384
    assert res["num_classes"] == 18
    assert len(res["probabilities"]) == 18
    assert np.isclose(sum(res["probabilities"]), 1.0, atol=1e-4)

    candidates = res["candidates"]
    assert len(candidates) == 18
    assert candidates[0]["class_name"] == res["predicted_class"]
    assert np.isclose(candidates[0]["probability"], res["confidence"])


# ===========================================================================
# 5. API Integration Tests
# ===========================================================================
def test_api_health_endpoint():
    """Tests /api/v1/health reports both models available."""
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["models_available"]["turmeric"] is True
    assert data["models_available"]["citrus"] is True


def test_api_diagnose_endpoint_turmeric():
    """Tests POST /api/v1/diagnose with turmeric image."""
    client = TestClient(app)
    sample_bytes = create_sample_leaf_bytes()

    response = client.post(
        "/api/v1/diagnose",
        files={"file": ("leaf.jpg", sample_bytes, "image/jpeg")},
        data={"crop": "turmeric", "language": "en"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["crop"] == "turmeric"
    assert "predicted_class" in data["prediction"]
    assert data["prediction"]["confidence"] > 0
    assert isinstance(data["calibration"]["is_active"], bool)
    assert len(data["prediction"]["candidates"]) == 4


def test_api_diagnose_endpoint_citrus():
    """Tests POST /api/v1/diagnose with citrus image."""
    client = TestClient(app)
    sample_bytes = create_sample_leaf_bytes()

    response = client.post(
        "/api/v1/diagnose",
        files={"file": ("citrus_leaf.jpg", sample_bytes, "image/jpeg")},
        data={"crop": "citrus", "language": "en"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["crop"] == "citrus"
    assert "predicted_class" in data["prediction"]
    assert data["prediction"]["confidence"] > 0
    assert isinstance(data["calibration"]["is_active"], bool)
    assert len(data["prediction"]["candidates"]) == 18
