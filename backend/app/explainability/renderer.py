"""
renderer.py - LeafLens Grad-CAM Overlay Renderer

Renders transparent, publication-quality heatmaps overlaid on original images:
- Aligned precisely with original image resolution
- Transparent blending preserving natural leaf texture in low-attention areas
- Warm color scale highlighting focused regions
- PNG base64 encoding ready for frontend display
"""

import io
import base64
import logging
from typing import Tuple, Optional
import numpy as np
from PIL import Image
import cv2

logger = logging.getLogger("LeafLens.GradCAMRenderer")


def render_gradcam_overlay(
    pil_image: Image.Image,
    heatmap: np.ndarray,
    colormap: int = cv2.COLORMAP_JET,
) -> str:
    """
    Renders transparent Grad-CAM heatmap over original PIL image and encodes as PNG base64.

    Args:
        pil_image: Original uploaded image (RGB).
        heatmap: 2D numpy array of shape (height, width) with values in [0.0, 1.0].
        colormap: OpenCV colormap constant (default: COLORMAP_JET).

    Returns:
        Base64-encoded PNG string (without data URI prefix).
    """
    orig_w, orig_h = pil_image.size
    h_h, h_w = heatmap.shape

    if (orig_w, orig_h) != (h_w, h_h):
        # Resize heatmap if shape slightly diverges
        heatmap = cv2.resize(heatmap, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)

    # Convert PIL Image to RGB numpy array
    rgb_img = np.array(pil_image.convert("RGB"), dtype=np.uint8)

    # Apply colormap to normalized heatmap
    heatmap_uint8 = (np.clip(heatmap, 0.0, 1.0) * 255.0).astype(np.uint8)
    colored_heatmap = cv2.applyColorMap(heatmap_uint8, colormap)
    colored_heatmap_rgb = cv2.cvtColor(colored_heatmap, cv2.COLOR_BGR2RGB)

    # Per-pixel alpha blending:
    # Low-attention areas (heatmap ~ 0) remain largely transparent (alpha ~ 0.05 - 0.15),
    # while high-attention areas (heatmap ~ 1.0) receive vivid warmth (alpha ~ 0.55).
    alpha = np.clip(heatmap * 0.55, 0.08, 0.55)[:, :, np.newaxis]
    blended = (rgb_img.astype(np.float32) * (1.0 - alpha) + colored_heatmap_rgb.astype(np.float32) * alpha)
    blended = np.clip(blended, 0.0, 255.0).astype(np.uint8)

    # Convert back to PIL Image and save to PNG bytes (compress_level=1 for CPU responsiveness)
    blended_pil = Image.fromarray(blended)
    buffer = io.BytesIO()
    blended_pil.save(buffer, format="PNG", compress_level=1)
    png_bytes = buffer.getvalue()

    return base64.b64encode(png_bytes).decode("utf-8")
