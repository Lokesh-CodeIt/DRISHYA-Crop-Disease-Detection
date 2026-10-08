"""
inference_service.py - LeafLens Unified CPU PyTorch Inference Engine

Manages CPU inference sessions for Turmeric (ConvNeXt-Tiny) and Citrus (EfficientNetV2-S).
Loads trained model weights once at startup via FastAPI lifespan.
Executes deterministic crop-aware preprocessing and softmax inference.
Exposes model references for downstream Grad-CAM hooks.
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image
import numpy as np
import torch
import torch.nn as nn

from ..ml.registry import (
    MODEL_REGISTRY,
    ModelConfig,
    get_active_model_config,
    get_registered_crops,
)
from ..ml.model_builder import load_trained_model, get_target_conv_layer
from ..preprocessing.image_pipeline import preprocess_image_bytes, ImagePreprocessingError

logger = logging.getLogger("LeafLens.InferenceService")


class InferenceService:
    """Manages active deep learning model weights and handles CPU inference."""

    def __init__(self):
        self.models: Dict[str, nn.Module] = {}
        self.configs: Dict[str, ModelConfig] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.class_mappings: Dict[str, Dict[str, int]] = {}
        self.idx_to_class: Dict[str, List[str]] = {}
        self.is_initialized = False

    def initialize_models(self):
        """Loads active production checkpoints for Turmeric and Citrus."""
        logger.info("Initializing LeafLens active ML models...")

        for crop in get_registered_crops():
            try:
                config = get_active_model_config(crop)
                model, meta = load_trained_model(config, map_location="cpu")

                self.models[crop] = model
                self.configs[crop] = config
                self.metadata[crop] = meta

                class_to_idx = config.get_class_to_idx()
                self.class_mappings[crop] = class_to_idx

                # Invert class_to_idx to get index-ordered class name list
                sorted_classes = [c for c, _ in sorted(class_to_idx.items(), key=lambda x: x[1])]
                self.idx_to_class[crop] = sorted_classes

                logger.info(
                    f"✓ Active model loaded: crop='{crop}' | arch='{config.architecture}' | "
                    f"seed={config.seed} | classes={config.num_classes} | resolution={config.img_size}x{config.img_size}"
                )
            except Exception as e:
                logger.error(f"✗ Failed to load model for crop '{crop}': {e}")

        self.is_initialized = True

    def is_model_available(self, crop: str) -> bool:
        """Checks if active model for crop is loaded and ready for inference."""
        return crop.lower().strip() in self.models

    def get_classes(self, crop: str) -> List[str]:
        """Returns ordered class names for a crop."""
        crop_lower = crop.lower().strip()
        return self.idx_to_class.get(crop_lower, [])

    def get_model(self, crop: str) -> nn.Module:
        """Retrieves raw nn.Module (used for Grad-CAM forward/backward hooks)."""
        crop_lower = crop.lower().strip()
        if not self.is_model_available(crop_lower):
            raise RuntimeError(f"Model for '{crop}' is not loaded.")
        return self.models[crop_lower]

    def get_config(self, crop: str) -> ModelConfig:
        """Retrieves ModelConfig for a crop."""
        crop_lower = crop.lower().strip()
        if crop_lower not in self.configs:
            raise RuntimeError(f"Config for '{crop}' not found.")
        return self.configs[crop_lower]

    def get_model_info(self, crop: str) -> Dict[str, Any]:
        """Returns diagnostic and version info for a crop model."""
        crop_lower = crop.lower().strip()
        if not self.is_model_available(crop_lower):
            return {"available": False, "crop": crop}

        cfg = self.configs[crop_lower]
        meta = self.metadata.get(crop_lower, {})
        return {
            "available": True,
            "crop": crop_lower,
            "architecture": cfg.architecture,
            "seed": cfg.seed,
            "img_size": cfg.img_size,
            "num_classes": cfg.num_classes,
            "classes": self.idx_to_class[crop_lower],
            "checkpoint_epoch": meta.get("epoch"),
            "val_macro_f1": meta.get("val_macro_f1"),
            "val_accuracy": meta.get("val_accuracy"),
            "grad_cam_layer": cfg.grad_cam_layer,
        }

    def run_inference(self, crop: str, input_tensor: np.ndarray) -> np.ndarray:
        """
        Executes raw model forward pass on normalized tensor shape (1, 3, H, W).
        Returns numpy array of raw logits of shape (1, num_classes).
        """
        crop_lower = crop.lower().strip()
        if not self.is_model_available(crop_lower):
            raise RuntimeError(f"Model for '{crop}' is not available.")

        model = self.models[crop_lower]
        with torch.no_grad():
            t = torch.from_numpy(input_tensor).float()
            logits = model(t)
            return logits.cpu().numpy()

    def predict(self, image_bytes: bytes, crop: str) -> Dict[str, Any]:
        """
        End-to-end inference execution:
        1. Validates crop
        2. Applies deterministic crop-aware preprocessing
        3. Executes forward pass without gradients
        4. Calculates softmax probabilities
        5. Returns structured prediction data
        """
        crop_lower = crop.lower().strip()
        if crop_lower not in ["turmeric", "citrus"]:
            raise ValueError(f"Unsupported crop '{crop}'. Must be 'turmeric' or 'citrus'.")

        if not self.is_model_available(crop_lower):
            raise RuntimeError(f"Active model for crop '{crop}' is not currently loaded in memory.")

        model = self.models[crop_lower]
        config = self.configs[crop_lower]
        classes = self.idx_to_class[crop_lower]

        # 1. Crop-aware preprocessing (224x224 for turmeric, 384x384 for citrus)
        batch_tensor_np, pil_image = preprocess_image_bytes(image_bytes, crop=crop_lower)

        # 2. Forward pass
        with torch.no_grad():
            tensor_torch = torch.from_numpy(batch_tensor_np).float()
            logits = model(tensor_torch)
            probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

        # 3. Identify top prediction
        top_idx = int(np.argmax(probs))
        confidence = float(probs[top_idx])
        predicted_class = classes[top_idx]

        # 4. Ranked candidate probabilities
        candidates = []
        for idx, cls_name in enumerate(classes):
            candidates.append({
                "class_name": cls_name,
                "probability": float(probs[idx]),
                "raw_probability": float(probs[idx]),
            })
        candidates.sort(key=lambda x: x["probability"], reverse=True)

        return {
            "crop": crop_lower,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "candidates": candidates,
            "raw_logits": logits[0].cpu().numpy().tolist(),
            "probabilities": probs.tolist(),
            "model_name": config.architecture,
            "seed": config.seed,
            "img_size": config.img_size,
            "num_classes": config.num_classes,
            "classes": classes,
            "pil_image": pil_image,
            "input_tensor": batch_tensor_np,
        }


inference_service = InferenceService()
