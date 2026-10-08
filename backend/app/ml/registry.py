"""
registry.py - LeafLens Centralized Model Registry

Defines configurations for all model artifacts across Turmeric and Citrus crops.
Policy:
- Turmeric: Seeds 42, 123, and 7 are all registered. Only Seed 42 is ACTIVE for inference.
  Seeds 123 and 7 are on standby for future multi-seed ensembling / comparison.
- Citrus: Seed 42 is registered and ACTIVE for inference.
- Checkpoint/metadata class mappings are authoritative.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import logging

logger = logging.getLogger("LeafLens.ModelRegistry")

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


@dataclass
class ModelConfig:
    crop: str
    architecture: str
    seed: int
    img_size: int
    num_classes: int
    is_active: bool
    status: str
    checkpoint_path: Optional[Path] = None
    metadata_path: Optional[Path] = None
    source_archive: Optional[str] = None
    internal_archive_path: Optional[str] = None
    grad_cam_layer: str = "features.7"
    notes: str = ""
    _class_to_idx: Optional[Dict[str, int]] = field(default=None, repr=False)

    def get_class_to_idx(self) -> Dict[str, int]:
        """
        Retrieves authoritative class-to-index mapping from metadata file
        or directly by reading checkpoint header.
        """
        if self._class_to_idx is not None:
            return self._class_to_idx

        # 1. Try reading from model_metadata.json if available
        if self.metadata_path and self.metadata_path.exists():
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    if "class_to_idx" in meta and isinstance(meta["class_to_idx"], dict):
                        self._class_to_idx = meta["class_to_idx"]
                        return self._class_to_idx
            except Exception as e:
                logger.warning(f"Failed to read class_to_idx from metadata {self.metadata_path}: {e}")

        # 2. Try reading from checkpoint file
        if self.checkpoint_path and self.checkpoint_path.exists():
            try:
                import torch
                ckpt = torch.load(self.checkpoint_path, map_location="cpu", weights_only=False)
                if isinstance(ckpt, dict) and "class_to_idx" in ckpt:
                    self._class_to_idx = ckpt["class_to_idx"]
                    return self._class_to_idx
            except Exception as e:
                logger.warning(f"Failed to read class_to_idx from checkpoint {self.checkpoint_path}: {e}")

        # 3. Fallback: Default canonical mappings verified in Phase 3/4 taxonomy
        if self.crop == "turmeric":
            self._class_to_idx = {
                "Dry Leaf": 0,
                "Healthy": 1,
                "Leaf Blotch": 2,
                "Leaf Spot": 3,
            }
        elif self.crop == "citrus":
            self._class_to_idx = {
                "Algal_Leaf_Spot": 0,
                "Anthracnose": 1,
                "Bacterial Blight": 2,
                "Black Spot": 3,
                "Citrus Canker": 4,
                "Citrus Hindu Mite": 5,
                "Citrus Leafminer": 6,
                "Citrus_Pest": 7,
                "Citrus_Scab": 8,
                "Curl Leaf": 9,
                "Dry Leaf": 10,
                "Greening": 11,
                "Healthy": 12,
                "Lemon_Sooty_Mold": 13,
                "Melanose": 14,
                "Spider Mites": 15,
                "Swallowtail Larval Herbivory (Deficiency)": 16,
                "Yellow_Spot": 17,
            }
        else:
            self._class_to_idx = {}

        return self._class_to_idx

    def get_classes(self) -> List[str]:
        """Returns sorted list of class names ordered by their integer index."""
        c2i = self.get_class_to_idx()
        sorted_pairs = sorted(c2i.items(), key=lambda x: x[1])
        return [cls_name for cls_name, _ in sorted_pairs]


# ===========================================================================
# Central Model Registry Definitions
# ===========================================================================
MODEL_REGISTRY: Dict[str, Dict[int, ModelConfig]] = {
    "turmeric": {
        42: ModelConfig(
            crop="turmeric",
            architecture="convnext_tiny",
            seed=42,
            img_size=224,
            num_classes=4,
            is_active=True,
            status="active",
            checkpoint_path=PROJECT_ROOT / "ml" / "models" / "turmeric" / "convnext_tiny" / "seed_42" / "best_model.pt",
            metadata_path=PROJECT_ROOT / "ml" / "models" / "turmeric" / "convnext_tiny" / "seed_42" / "model_metadata.json",
            grad_cam_layer="features.7",
            notes="Active production model for Turmeric crop diagnosis.",
        ),
        123: ModelConfig(
            crop="turmeric",
            architecture="convnext_tiny",
            seed=123,
            img_size=224,
            num_classes=4,
            is_active=False,
            status="standby_for_ensemble",
            source_archive="PROJECT_ARTIFACTS/turmeric/CROP_DETECTION_RESULTS-20261006T095833Z-1-001.zip",
            internal_archive_path="CROP_DETECTION_RESULTS/turmeric/convnext_tiny/seed_123/best_model.pt",
            grad_cam_layer="features.7",
            notes="Completed seed training run; preserved on standby for future multi-seed ensembling.",
        ),
        7: ModelConfig(
            crop="turmeric",
            architecture="convnext_tiny",
            seed=7,
            img_size=224,
            num_classes=4,
            is_active=False,
            status="standby_for_ensemble",
            source_archive="PROJECT_ARTIFACTS/turmeric/CROP_DETECTION_RESULTS-20261006T095833Z-1-001.zip",
            internal_archive_path="CROP_DETECTION_RESULTS/turmeric/convnext_tiny/seed_7/best_model.pt",
            grad_cam_layer="features.7",
            notes="Completed seed training run; preserved on standby for future multi-seed ensembling.",
        ),
    },
    "citrus": {
        42: ModelConfig(
            crop="citrus",
            architecture="efficientnet_v2_s",
            seed=42,
            img_size=384,
            num_classes=18,
            is_active=True,
            status="active",
            checkpoint_path=PROJECT_ROOT / "ml" / "models" / "citrus" / "efficientnet_v2_s" / "seed_42" / "best_model.pt",
            metadata_path=PROJECT_ROOT / "ml" / "models" / "citrus" / "efficientnet_v2_s" / "seed_42" / "model_metadata.json",
            source_archive="PROJECT_ARTIFACTS/citrus/CROP_DETECTION_CHECKPOINTS-20261006T101034Z-1-001.zip",
            internal_archive_path="CROP_DETECTION_CHECKPOINTS/citrus/efficientnet_v2_s/seed_42/best_model.pt",
            grad_cam_layer="features.7",
            notes="Active production model for Citrus crop diagnosis (Epoch 38, 40 epochs trained).",
        ),
    },
}


def get_active_model_config(crop: str) -> ModelConfig:
    """Retrieves the active ModelConfig for a crop."""
    crop_lower = crop.lower().strip()
    if crop_lower not in MODEL_REGISTRY:
        raise ValueError(f"Unsupported crop '{crop}'. Registered crops: {list(MODEL_REGISTRY.keys())}")

    for seed, config in MODEL_REGISTRY[crop_lower].items():
        if config.is_active:
            return config

    raise RuntimeError(f"No active model configuration marked for crop '{crop}'")


def get_model_config(crop: str, seed: int) -> ModelConfig:
    """Retrieves a specific seed ModelConfig for a crop."""
    crop_lower = crop.lower().strip()
    if crop_lower not in MODEL_REGISTRY:
        raise ValueError(f"Unsupported crop '{crop}'. Registered crops: {list(MODEL_REGISTRY.keys())}")
    if seed not in MODEL_REGISTRY[crop_lower]:
        raise ValueError(f"Seed {seed} not registered for crop '{crop}'. Available seeds: {list(MODEL_REGISTRY[crop_lower].keys())}")
    return MODEL_REGISTRY[crop_lower][seed]


def get_registered_crops() -> List[str]:
    """Returns list of all registered crops."""
    return list(MODEL_REGISTRY.keys())


def get_registered_seeds(crop: str) -> List[int]:
    """Returns list of all registered seeds for a given crop."""
    crop_lower = crop.lower().strip()
    if crop_lower not in MODEL_REGISTRY:
        return []
    return list(MODEL_REGISTRY[crop_lower].keys())
