"""
model_builder.py - LeafLens Reusable Model Construction & Weight Loader

Constructs deep learning architectures for CPU evaluation and loads trained checkpoints:
- ConvNeXt-Tiny (Turmeric 4 classes)
- EfficientNetV2-S (Citrus 18 classes)

Key Design:
- Does NOT download pretrained ImageNet weights from the internet; builds architecture cleanly
  and populates weights from local verified checkpoints.
- Sets model to eval() and requires_grad=False.
- Decoupled from training scripts.
"""

import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

import torch
import torch.nn as nn
from torchvision import models

from .registry import ModelConfig

logger = logging.getLogger("LeafLens.ModelBuilder")


def build_model_architecture(architecture: str, num_classes: int) -> nn.Module:
    """
    Constructs model architecture with replacement classification head
    matching the trained LeafLens topologies.
    """
    arch = architecture.lower().strip()

    if arch == "convnext_tiny":
        model = models.convnext_tiny(weights=None)
        in_features = model.classifier[2].in_features  # 768
        model.classifier[2] = nn.Linear(in_features, num_classes)
        logger.debug(f"Instantiated ConvNeXt-Tiny with Linear({in_features}, {num_classes})")
        return model

    elif arch == "efficientnet_v2_s":
        model = models.efficientnet_v2_s(weights=None)
        in_features = model.classifier[1].in_features  # 1280
        model.classifier[1] = nn.Linear(in_features, num_classes)
        logger.debug(f"Instantiated EfficientNetV2-S with Linear({in_features}, {num_classes})")
        return model

    else:
        raise ValueError(f"Unsupported model architecture: '{architecture}'. Supported: ['convnext_tiny', 'efficientnet_v2_s']")


def load_trained_model(
    config: ModelConfig,
    map_location: str = "cpu",
) -> Tuple[nn.Module, Dict[str, Any]]:
    """
    Loads checkpoint weights from disk into the specified architecture.
    Returns:
        (model in eval mode with no gradients, checkpoint metadata dictionary)
    """
    if not config.checkpoint_path or not config.checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint file not found for crop '{config.crop}', seed {config.seed}: {config.checkpoint_path}"
        )

    logger.info(f"Loading checkpoint for {config.crop} ({config.architecture}, seed {config.seed}) from {config.checkpoint_path}")

    checkpoint = torch.load(config.checkpoint_path, map_location=map_location, weights_only=False)

    if not isinstance(checkpoint, dict) or "model_state_dict" not in checkpoint:
        raise ValueError(f"Invalid checkpoint format in {config.checkpoint_path}: expected dictionary containing 'model_state_dict'")

    # Build architecture
    model = build_model_architecture(config.architecture, config.num_classes)

    # Load weights
    model.load_state_dict(checkpoint["model_state_dict"])

    # Prepare for evaluation
    model.eval()
    for param in model.parameters():
        param.requires_grad = False

    logger.info(f"Successfully loaded and set to eval mode: {config.crop} ({config.architecture}, seed {config.seed})")

    # Extract metadata summary
    metadata = {
        "crop": checkpoint.get("crop", config.crop),
        "model": checkpoint.get("model", config.architecture),
        "seed": checkpoint.get("seed", config.seed),
        "epoch": checkpoint.get("epoch"),
        "val_macro_f1": checkpoint.get("val_macro_f1"),
        "val_accuracy": checkpoint.get("val_accuracy"),
        "img_size": checkpoint.get("img_size", config.img_size),
        "num_classes": config.num_classes,
        "class_to_idx": checkpoint.get("class_to_idx", config.get_class_to_idx()),
    }

    return model, metadata


def get_target_conv_layer(model: nn.Module, layer_path: str = "features.7") -> Optional[nn.Module]:
    """
    Retrieves submodule by dot-separated path (e.g. 'features.7')
    for Grad-CAM activation and gradient tapping.
    """
    submodule = model
    try:
        for part in layer_path.split("."):
            if part.isdigit():
                submodule = submodule[int(part)]
            else:
                submodule = getattr(submodule, part)
        return submodule
    except Exception as e:
        logger.warning(f"Could not resolve layer path '{layer_path}' in model: {e}")
        return None
