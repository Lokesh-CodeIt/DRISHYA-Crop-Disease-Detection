"""
Unit tests for LeafLens image preprocessing and validation pipeline.
"""

import io
import pytest
import numpy as np
from PIL import Image
from backend.app.preprocessing.image_pipeline import preprocess_image_bytes, ImagePreprocessingError


def create_dummy_image_bytes(format="JPEG", size=(300, 300), color=(100, 150, 200)) -> bytes:
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def test_valid_image_preprocessing():
    img_bytes = create_dummy_image_bytes()
    tensor, pil_img = preprocess_image_bytes(img_bytes, target_size=(224, 224))

    assert isinstance(tensor, np.ndarray)
    assert tensor.shape == (1, 3, 224, 224)
    assert tensor.dtype == np.float32
    assert pil_img.size == (300, 300)


def test_corrupted_image_raises_error():
    corrupted_bytes = b"not-a-valid-image-stream-content"
    with pytest.raises(ImagePreprocessingError):
        preprocess_image_bytes(corrupted_bytes)
