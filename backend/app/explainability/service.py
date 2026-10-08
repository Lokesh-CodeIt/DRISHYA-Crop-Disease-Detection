"""
service.py - LeafLens Centralized Explainability Orchestration Service

Orchestrates:
1. Retrieval of active PyTorch model from inference_service (zero model reload)
2. Reuse of preprocessed input tensor and original PIL image (zero duplicate preprocessing)
3. Standard Grad-CAM calculation on target class logit
4. Transparent overlay rendering on original image
5. Real attention-region extraction (at most 3 distinct regions)
6. Latency tracking and fault-tolerant error containment

Guarantees:
- If Grad-CAM fails for any reason, this service logs the error and returns None.
- It will NEVER raise an exception that interrupts user diagnosis.
"""

import time
import logging
from typing import Optional, Dict, Any
import numpy as np
from PIL import Image

from ..ml.registry import get_active_model_config
from ..services.inference_service import inference_service
from ..preprocessing.image_pipeline import preprocess_image_bytes
from ..models.schemas import GradCAMExplanation, AttentionRegion
from .gradcam import GradCAMExplainer
from .renderer import render_gradcam_overlay
from .region_extractor import extract_attention_regions

logger = logging.getLogger("LeafLens.ExplainabilityService")


class ExplainabilityService:
    """Production service for live Grad-CAM and attention region extraction."""

    def __init__(self):
        self.explainer = GradCAMExplainer()

    def generate_explanation(
        self,
        image_bytes: bytes,
        crop: str,
        predicted_class: str,
        input_tensor: Optional[np.ndarray] = None,
        pil_image: Optional[Image.Image] = None,
    ) -> Optional[GradCAMExplanation]:
        """
        Generates full Grad-CAM explanation package for the predicted class.

        Args:
            image_bytes: Raw uploaded image bytes.
            crop: 'turmeric' or 'citrus'.
            predicted_class: The predicted class label returned by diagnosis.
            input_tensor: Optional preprocessed input tensor from inference step.
            pil_image: Optional original PIL image from inference step.

        Returns:
            GradCAMExplanation object, or None if explanation fails.
        """
        t_start = time.perf_counter()
        crop_lower = crop.lower().strip()

        try:
            # 1. Retrieve active model and config from inference service
            if not inference_service.is_model_available(crop_lower):
                logger.warning(f"Active model for crop '{crop_lower}' is not loaded in inference_service.")
                return None

            model = inference_service.get_model(crop_lower)
            config = inference_service.get_config(crop_lower)
            class_to_idx = config.get_class_to_idx()

            if predicted_class not in class_to_idx:
                logger.warning(
                    f"Predicted class '{predicted_class}' not found in class mapping for '{crop_lower}'. "
                    f"Available classes: {list(class_to_idx.keys())}"
                )
                return None

            target_class_idx = class_to_idx[predicted_class]

            # 2. Reuse preprocessed input or preprocess from image bytes
            if input_tensor is None or pil_image is None:
                input_tensor, pil_image = preprocess_image_bytes(image_bytes, crop=crop_lower)

            orig_w, orig_h = pil_image.size

            # 3. Target convolutional layer
            target_layer = config.grad_cam_layer or "features.7"

            # 4. Compute standard Grad-CAM heatmap
            heatmap = self.explainer.generate_heatmap(
                model=model,
                target_layer_name=target_layer,
                input_tensor=input_tensor,
                target_class_idx=target_class_idx,
                orig_size=(orig_w, orig_h),
            )

            # 5. Render transparent overlay on original image
            overlay_base64 = render_gradcam_overlay(pil_image=pil_image, heatmap=heatmap)

            # 6. Extract real model attention regions
            regions, unavail_reason = extract_attention_regions(
                pil_image=pil_image,
                heatmap=heatmap,
                max_regions=3,
            )

            # 7. Summary metrics (backward compatibility & diagnostics)
            mean_intensity = round(float(np.mean(heatmap)), 4)
            high_attn_area = round(float(np.mean(heatmap >= 0.5)), 4)
            focus_score = round(float(np.max(heatmap) - np.mean(heatmap)), 4)

            elapsed_ms = round((time.perf_counter() - t_start) * 1000.0, 2)

            return GradCAMExplanation(
                method="Grad-CAM",
                target_class=predicted_class,
                target_layer=target_layer,
                overlay_base64=overlay_base64,
                image_width=orig_w,
                image_height=orig_h,
                regions=regions,
                processing_time_ms=elapsed_ms,
                explanation_available=True,
                reason=unavail_reason,
                mean_intensity=mean_intensity,
                high_attention_area_fraction=high_attn_area,
                focus_score=focus_score,
            )

        except Exception as e:
            logger.error(f"Grad-CAM explanation generation failed gracefully: {e}", exc_info=True)
            return None


explainability_service = ExplainabilityService()
