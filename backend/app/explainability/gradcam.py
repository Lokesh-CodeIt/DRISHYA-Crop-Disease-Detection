"""
gradcam.py - LeafLens Production-Safe Standard Grad-CAM Engine

Implements standard Grad-CAM (Selvaraju et al., 2017):
1. Takes preprocessed tensor (1, 3, H, W)
2. Executes forward pass with gradient tracking on input tensor
3. Targets predicted class LOGIT (raw uncalibrated logit score)
4. Computes gradient of predicted class logit w.r.t target spatial feature map
5. Global-Average-Pools gradients across spatial dimensions (w_k)
6. Computes weighted combination of feature activations
7. Applies ReLU to retain only features with positive contribution
8. Normalizes heatmap to [0.0, 1.0]
9. Interpolates heatmap to original image dimensions (W_orig, H_orig)

Safety Guarantees:
- Model parameters remain frozen with requires_grad=False.
- Hooks are registered temporarily and strictly removed in try...finally.
- Model gradients are zeroed and computation graph is released.
- Normal inference remains unaffected.
"""

import logging
from typing import Tuple, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from ..ml.model_builder import get_target_conv_layer

logger = logging.getLogger("LeafLens.GradCAM")


class GradCAMExplainer:
    """Computes standard Grad-CAM heatmaps for PyTorch vision models."""

    @staticmethod
    def generate_heatmap(
        model: nn.Module,
        target_layer_name: str,
        input_tensor: np.ndarray,
        target_class_idx: int,
        orig_size: Tuple[int, int],  # (orig_width, orig_height)
    ) -> np.ndarray:
        """
        Generates normalized [0.0, 1.0] 2D Grad-CAM heatmap matching orig_size.

        Args:
            model: Active PyTorch model in eval mode.
            target_layer_name: Dot-separated submodule path (e.g. 'features.7').
            input_tensor: Normalized numpy batch tensor of shape (1, 3, H, W).
            target_class_idx: Integer index of predicted target class.
            orig_size: (width, height) of the original uploaded image in pixels.

        Returns:
            2D numpy array of shape (orig_height, orig_width) with values in [0.0, 1.0].
        """
        orig_w, orig_h = orig_size
        target_layer = get_target_conv_layer(model, target_layer_name)
        if target_layer is None:
            raise ValueError(f"Could not resolve target layer '{target_layer_name}' in model.")

        activations = []
        gradients = []

        def forward_hook(module, inp, out):
            activations.append(out)

            def backward_hook(grad):
                gradients.append(grad)

            out.register_hook(backward_hook)
            return None

        # Prepare input tensor with requires_grad=True so activations form graph
        # Model parameters themselves remain requires_grad=False (100% frozen)
        if isinstance(input_tensor, np.ndarray):
            x = torch.from_numpy(input_tensor).float()
        else:
            x = input_tensor.clone().float()

        if x.dim() == 3:
            x = x.unsqueeze(0)

        x = x.detach().requires_grad_(True)

        hook_handle = target_layer.register_forward_hook(forward_hook)

        try:
            with torch.enable_grad():
                logits = model(x)

                if target_class_idx < 0 or target_class_idx >= logits.shape[1]:
                    raise ValueError(
                        f"Target class index {target_class_idx} out of bounds for model with {logits.shape[1]} outputs."
                    )

                # Target is strictly the predicted class raw LOGIT
                target_score = logits[0, target_class_idx]
                target_score.backward()

            if not activations or not gradients:
                raise RuntimeError("Failed to capture feature activations or gradients during Grad-CAM pass.")

            act = activations[0]   # Shape: (1, C, H_feat, W_feat)
            grad = gradients[0]  # Shape: (1, C, H_feat, W_feat)

            # Global Average Pooling of gradients over spatial dimensions (H_feat, W_feat)
            weights = torch.mean(grad, dim=(2, 3), keepdim=True)  # Shape: (1, C, 1, 1)

            # Weighted combination of forward activation maps
            cam = torch.sum(weights * act, dim=1, keepdim=True)  # Shape: (1, 1, H_feat, W_feat)

            # ReLU to keep only positive contributions
            cam = F.relu(cam)

            # Normalize to [0.0, 1.0]
            min_val = cam.min()
            max_val = cam.max()
            if (max_val - min_val) > 1e-8:
                cam = (cam - min_val) / (max_val - min_val)
            else:
                cam = torch.zeros_like(cam)

            # Interpolate to original image dimensions (orig_h, orig_w)
            cam_resized = F.interpolate(
                cam,
                size=(orig_h, orig_w),
                mode="bilinear",
                align_corners=False,
            )

            heatmap_np = cam_resized[0, 0].detach().cpu().numpy()
            return np.clip(heatmap_np, 0.0, 1.0).astype(np.float32)

        finally:
            # Mandatory cleanup: remove hook, zero any residual grads, release graph
            hook_handle.remove()
            model.zero_grad(set_to_none=True)
            del activations, gradients, x
