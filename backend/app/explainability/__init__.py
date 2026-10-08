"""
backend.app.explainability package

Production-safe Grad-CAM explainability and attention-region extraction for DRISHYA.
"""

from .gradcam import GradCAMExplainer
from .renderer import render_gradcam_overlay
from .region_extractor import extract_attention_regions
from .service import explainability_service, ExplainabilityService

__all__ = [
    "GradCAMExplainer",
    "render_gradcam_overlay",
    "extract_attention_regions",
    "explainability_service",
    "ExplainabilityService",
]
