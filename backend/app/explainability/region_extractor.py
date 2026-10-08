"""
region_extractor.py - LeafLens Real Attention-Region Extraction Engine

Extracts genuinely activated attention regions from Grad-CAM heatmaps:
1. Normalizes and analyzes spatial localization of activation
2. Derives deterministic high-attention threshold
3. Creates attention mask and applies morphological opening to filter noise
4. Detects connected components / external contours
5. Computes attention mass and ranks components
6. Selects at most 3 spatially distinct non-overlapping regions
7. Adds context padding (10-15%) clamped to original image dimensions
8. Crops original image pixels and encodes as JPEG base64 thumbnails

Terminology Rule:
These are "attention regions" or "higher-attention areas" representing model focus.
They are NOT claimed to be lesion segmentations or defect counts.
"""

import io
import base64
import logging
from typing import List, Tuple, Optional
import numpy as np
from PIL import Image
import cv2

from ..models.schemas import AttentionRegion

logger = logging.getLogger("LeafLens.RegionExtractor")


def compute_iou(box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]) -> float:
    """Computes Intersection over Union for two (x, y, w, h) boxes."""
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)

    inter_w = max(0, xi2 - xi1)
    inter_h = max(0, yi2 - yi1)
    inter_area = inter_w * inter_h

    area1 = w1 * h1
    area2 = w2 * h2
    union_area = area1 + area2 - inter_area

    if union_area <= 0:
        return 0.0
    return float(inter_area / union_area)


def extract_attention_regions(
    pil_image: Image.Image,
    heatmap: np.ndarray,
    max_regions: int = 3,
) -> Tuple[List[AttentionRegion], Optional[str]]:
    """
    Extracts up to max_regions spatially distinct attention regions from Grad-CAM heatmap.

    Args:
        pil_image: Original uploaded PIL image (RGB).
        heatmap: 2D numpy array of shape (height, width) with values in [0.0, 1.0].
        max_regions: Maximum number of distinct regions to retain (default: 3).

    Returns:
        Tuple of (list of AttentionRegion, diagnostic reason if empty).
    """
    orig_w, orig_h = pil_image.size
    total_area = orig_w * orig_h

    # Check 1: Diffuse / unlocalized check
    max_intensity = float(np.max(heatmap))
    if max_intensity < 0.25:
        logger.debug(f"Heatmap maximum intensity ({max_intensity:.3f}) below localization threshold.")
        return [], "attention_map_not_localized"

    # Check 2: Deterministic threshold derivation
    # Use 80th percentile or 0.40, whichever is higher, capped at 0.85 * max_intensity
    pct80 = float(np.percentile(heatmap, 80))
    threshold_val = max(0.40, pct80)
    if threshold_val >= max_intensity:
        threshold_val = 0.50 * max_intensity

    binary_mask = (heatmap >= threshold_val).astype(np.uint8) * 255

    # Check 3: Morphological cleanup to remove tiny isolated noise specks
    kernel_dim = max(5, int(min(orig_w, orig_h) * 0.015))
    if kernel_dim % 2 == 0:
        kernel_dim += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_dim, kernel_dim))
    mask_cleaned = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)

    # Check 4: Find connected contours
    contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return [], "attention_map_not_localized"

    # Minimum and maximum valid contour area guards
    min_contour_area = total_area * 0.002   # 0.2% of total image area
    max_contour_area = total_area * 0.80    # Reject if single component covers >80% of image

    candidates = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_contour_area or area > max_contour_area:
            continue

        bx, by, bw, bh = cv2.boundingRect(c)
        if bw < 15 or bh < 15:
            continue

        # Region attention score = mean heatmap value within the bounding box
        region_heatmap = heatmap[by : by + bh, bx : bx + bw]
        mean_attn = float(np.mean(region_heatmap))
        attention_mass = float(area * mean_attn)

        candidates.append({
            "contour": c,
            "bbox": (bx, by, bw, bh),
            "area": area,
            "attention_score": mean_attn,
            "attention_mass": attention_mass,
        })

    if not candidates:
        return [], "attention_map_not_localized"

    # Rank candidate contours by attention mass descending
    candidates.sort(key=lambda item: item["attention_mass"], reverse=True)

    # Select top spatially distinct regions using IoU suppression
    selected_boxes = []
    for cand in candidates:
        box = cand["bbox"]
        # Check overlap with already selected boxes
        overlap = any(compute_iou(box, sel["bbox"]) > 0.35 for sel in selected_boxes)
        if not overlap:
            selected_boxes.append(cand)
            if len(selected_boxes) >= max_regions:
                break

    # Context expansion and thumbnail extraction
    regions: List[AttentionRegion] = []
    for idx, cand in enumerate(selected_boxes):
        bx, by, bw, bh = cand["bbox"]

        # 12% margin expansion for context
        pad_x = int(bw * 0.12)
        pad_y = int(bh * 0.12)

        x1 = max(0, bx - pad_x)
        y1 = max(0, by - pad_y)
        x2 = min(orig_w, bx + bw + pad_x)
        y2 = min(orig_h, by + bh + pad_y)

        final_w = x2 - x1
        final_h = y2 - y1

        if final_w <= 0 or final_h <= 0:
            continue

        # Crop directly from original PIL image pixels
        crop_pil = pil_image.crop((x1, y1, x2, y2))

        # Encode crop as JPEG base64 thumbnail
        buf = io.BytesIO()
        crop_pil.save(buf, format="JPEG", quality=88)
        crop_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        regions.append(
            AttentionRegion(
                region_id=idx + 1,
                x=int(x1),
                y=int(y1),
                width=int(final_w),
                height=int(final_h),
                attention_score=round(float(cand["attention_score"]), 4),
                crop_base64=crop_base64,
            )
        )

    if not regions:
        return [], "attention_map_not_localized"

    return regions, None
