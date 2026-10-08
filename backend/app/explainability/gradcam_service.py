"""
gradcam_service.py - LeafLens Visual Explainability Service

Generates visual diagnostic overlays explaining which leaf regions informed the prediction.
Converts heatmaps to base64 JPEG strings for seamless React frontend rendering,
and measures attention metrics to quantify model focus.
"""

import io
import base64
from typing import Dict, Any, Tuple
from PIL import Image
import numpy as np
import cv2


class GradCAMVisualizer:
    """Utilities for rendering and quantifying visual explanations."""

    @staticmethod
    def overlay_heatmap(
        image: Image.Image,
        heatmap: np.ndarray,
        alpha: float = 0.45,
        colormap: int = cv2.COLORMAP_JET,
    ) -> Image.Image:
        """Overlays a 2D float heatmap [0, 1] onto the source PIL Image."""
        img_np = np.array(image.convert("RGB"))
        h, w, _ = img_np.shape

        # Resize heatmap to match image dimensions
        resized_cam = cv2.resize(heatmap, (w, h), interpolation=cv2.INTER_LINEAR)
        colored_cam = cv2.applyColorMap(np.uint8(255 * resized_cam), colormap)
        colored_cam = cv2.cvtColor(colored_cam, cv2.COLOR_BGR2RGB)

        blended = cv2.addWeighted(img_np, 1.0 - alpha, colored_cam, alpha, 0)
        return Image.fromarray(blended)

    @staticmethod
    def image_to_base64(image: Image.Image, format: str = "JPEG", quality: int = 90) -> str:
        """Encodes PIL Image to base64 data URI."""
        buffered = io.BytesIO()
        image.save(buffered, format=format, quality=quality)
        b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64_str}"

    @staticmethod
    def compute_attention_metrics(heatmap: np.ndarray, high_threshold: float = 0.5) -> Dict[str, float]:
        """Calculates attention energy distribution metrics."""
        high_mask = heatmap >= high_threshold
        mean_intensity = float(np.mean(heatmap))
        high_area_fraction = float(np.mean(high_mask))
        focus_score = float(np.sum(heatmap * high_mask) / (np.sum(heatmap) + 1e-8))

        return {
            "mean_intensity": round(mean_intensity, 4),
            "high_attention_area_fraction": round(high_area_fraction, 4),
            "focus_score": round(focus_score, 4),
        }


visualizer = GradCAMVisualizer()
