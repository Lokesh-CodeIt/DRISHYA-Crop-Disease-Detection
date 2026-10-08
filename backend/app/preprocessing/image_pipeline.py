"""
image_pipeline.py - LeafLens Web Inference Preprocessing Pipeline

Prepares uploaded user leaf photographs for deep learning inference.
Applies crop-aware resizing:
  - Turmeric: 224 x 224
  - Citrus:   384 x 384
Applies identical RGB conversion, RGBA transparency alpha-blending,
and ImageNet channel normalization as utilized during training.
"""

import io
from typing import Tuple, Optional, Dict
from PIL import Image
import numpy as np


class ImagePreprocessingError(Exception):
    """Raised when an uploaded file fails validation or preprocessing."""
    pass


# Canonical resolution mapping per crop
CROP_INPUT_SIZES: Dict[str, Tuple[int, int]] = {
    "turmeric": (224, 224),
    "citrus": (384, 384),
}


def get_crop_target_size(crop: str) -> Tuple[int, int]:
    """Resolves standard input dimensions for a given crop."""
    crop_lower = crop.lower().strip()
    if crop_lower in CROP_INPUT_SIZES:
        return CROP_INPUT_SIZES[crop_lower]
    raise ValueError(f"Unknown crop '{crop}'. Supported crops: {list(CROP_INPUT_SIZES.keys())}")


def preprocess_image_bytes(
    image_bytes: bytes,
    target_size: Optional[Tuple[int, int]] = None,
    crop: Optional[str] = None,
    mean: Tuple[float, float, float] = (0.485, 0.456, 0.406),
    std: Tuple[float, float, float] = (0.229, 0.224, 0.225),
) -> Tuple[np.ndarray, Image.Image]:
    """
    Validates and transforms raw bytes into:
    1. Normalized float32 numpy tensor of shape (1, 3, H, W)
    2. Original RGB PIL Image for Grad-CAM overlay compositing

    If 'crop' is provided, target_size is determined automatically:
      turmeric -> (224, 224)
      citrus   -> (384, 384)
    """
    if not image_bytes or len(image_bytes) == 0:
        raise ImagePreprocessingError("Uploaded image byte stream is empty.")

    # Resolve target dimensions
    if target_size is not None:
        resolved_size = target_size
    elif crop is not None:
        resolved_size = get_crop_target_size(crop)
    else:
        resolved_size = (224, 224)

    try:
        # Load and verify integrity
        stream = io.BytesIO(image_bytes)
        img = Image.open(stream)
        img.verify()

        # Reopen for pixel processing
        stream.seek(0)
        img = Image.open(stream)

        # Convert to RGB cleanly handling alpha channels & palettes
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            alpha_img = img.convert("RGBA")
            canvas = Image.new("RGB", alpha_img.size, (255, 255, 255))
            canvas.paste(alpha_img, mask=alpha_img.split()[3])
            rgb_img = canvas
        else:
            rgb_img = img.convert("RGB")

    except Exception as e:
        raise ImagePreprocessingError(f"Uploaded file is not a valid, readable image: {str(e)}")

    # Resize to target input dimensions
    resized_img = rgb_img.resize(resolved_size, Image.Resampling.BILINEAR)

    # Normalize: Convert to [0, 1] range float32
    img_array = np.array(resized_img, dtype=np.float32) / 255.0

    # Apply ImageNet channel normalization: (x - mean) / std
    mean_arr = np.array(mean, dtype=np.float32)
    std_arr = np.array(std, dtype=np.float32)
    norm_img = (img_array - mean_arr) / std_arr

    # Rearrange dimensions from (H, W, C) to (C, H, W)
    chw_img = np.transpose(norm_img, (2, 0, 1))

    # Add batch dimension: (1, C, H, W)
    batch_tensor = np.expand_dims(chw_img, axis=0).astype(np.float32)

    return batch_tensor, rgb_img
