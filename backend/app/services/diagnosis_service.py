"""
diagnosis_service.py - LeafLens Complete Diagnosis Pipeline Orchestrator

Integrates:
1. Unified CPU PyTorch Inference (Crop-Aware Preprocessing + Softmax)
2. Image SHA-256 fingerprinting and telemetry tracking
3. Calibration status reporting (marked inactive per Rule H)
4. Expert-Vetted Multilingual Disease Advisory Retrieval
5. SQLite Prediction History Persistence
"""

import time
import json
import hashlib
import logging
from typing import Optional
from sqlalchemy.orm import Session

import numpy as np
from ..models.schemas import (
    CropType,
    Language,
    DiagnosisResponse,
    PredictionResult,
    CandidateClass,
    CalibrationInfo,
    GradCAMExplanation,
)
from ..services.inference_service import inference_service
from ..calibration.temperature_scaler import scaler
from ..explainability import explainability_service
from ..advisory.repository import advisory_repository
from ..knowledge import get_condition_knowledge
from ..db.repository import history_repo
from ..db.database import get_db_context
from ..utils.config import settings

logger = logging.getLogger("LeafLens.DiagnosisService")


class DiagnosisService:
    """Orchestrates end-to-end explainable crop diagnosis workflow."""

    def diagnose(
        self,
        image_bytes: bytes,
        crop: CropType,
        language: Language = Language.ENGLISH,
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
    ) -> DiagnosisResponse:
        crop_val = crop.value
        t_start = time.perf_counter()

        # Step 1: Compute Image SHA-256 fingerprint (transient, image not stored)
        image_sha256 = hashlib.sha256(image_bytes).hexdigest()

        # Step 2: Execute Unified Inference Pipeline
        inf_result = inference_service.predict(image_bytes=image_bytes, crop=crop_val)
        processing_time_ms = round((time.perf_counter() - t_start) * 1000.0, 2)

        # Step 3: Calibrate Confidence via Temperature Scaling
        raw_logits_np = np.array([inf_result["raw_logits"]], dtype=np.float32)
        calib_result = scaler.calibrate(
            raw_logits_np,
            crop=crop_val,
            threshold=settings.UNCERTAINTY_REJECTION_THRESHOLD,
        )

        classes_list = inf_result.get("classes") or [c["class_name"] for c in inf_result["candidates"]]

        # Build candidate probabilities breakdown
        candidates = []
        for c in inf_result["candidates"]:
            cls_name = c["class_name"]
            calib_p = None
            if calib_result.is_active and calib_result.calibrated_probs is not None and cls_name in classes_list:
                cls_idx = classes_list.index(cls_name)
                calib_p = float(calib_result.calibrated_probs[cls_idx])

            candidates.append(
                CandidateClass(
                    class_name=cls_name,
                    probability=c["probability"],
                    raw_probability=c["raw_probability"],
                    calibrated_probability=calib_p,
                )
            )

        predicted_class_name = inf_result["predicted_class"]
        raw_confidence = inf_result["confidence"]
        calibrated_conf = calib_result.calibrated_confidence if calib_result.is_active else None
        is_rejected = calib_result.is_rejected
        rejection_reason = calib_result.rejection_reason if is_rejected else None

        prediction_result = PredictionResult(
            predicted_class=predicted_class_name,
            confidence=raw_confidence,
            calibrated_confidence=calibrated_conf,
            is_rejected=is_rejected,
            rejection_reason=rejection_reason,
            candidates=candidates,
        )

        # Step 4: Calibration Status
        calibration_info = CalibrationInfo(
            temperature_applied=calib_result.temperature_applied if calib_result.is_active else None,
            raw_confidence=raw_confidence,
            calibrated_confidence=calibrated_conf,
            is_active=calib_result.is_active,
            is_uncertain=is_rejected,
            rejection_threshold=settings.UNCERTAINTY_REJECTION_THRESHOLD,
        )

        # Step 5: Advisory lookup (legacy compatibility)
        disease_slug = f"{crop_val}_{predicted_class_name.lower().replace(' ', '_')}"
        advisory_rec = advisory_repository.get_advisory(
            disease_id=disease_slug,
            crop=crop_val,
            language=language.value,
        )
        advisory_id_val = advisory_rec.disease_id if advisory_rec else None

        # Step 5.1: Condition Knowledge & Safe Advisory Layer (Step D)
        knowledge_obj = None
        try:
            knowledge_obj = get_condition_knowledge(
                crop=crop_val,
                predicted_class=predicted_class_name,
                language=language.value,
                is_rejected=is_rejected,
            )
        except Exception as k_err:
            logger.error(f"Failed to retrieve condition knowledge: {k_err}", exc_info=True)
            knowledge_obj = None

        # Step 6: Grad-CAM Explainability (Isolated, fault-tolerant)
        explanation_obj = None
        try:
            explanation_obj = explainability_service.generate_explanation(
                image_bytes=image_bytes,
                crop=crop_val,
                predicted_class=predicted_class_name,
                input_tensor=inf_result.get("input_tensor"),
                pil_image=inf_result.get("pil_image"),
            )
        except Exception as exp_err:
            logger.error(f"Grad-CAM explanation failed gracefully: {exp_err}", exc_info=True)
            explanation_obj = None

        total_processing_time_ms = round((time.perf_counter() - t_start) * 1000.0, 2)

        # Step 7: Persist Prediction to Database (Fault-tolerant)
        prediction_id = None
        try:
            record_data = {
                "user_id": user_id,
                "crop": crop_val,
                "predicted_class": predicted_class_name,
                "confidence": raw_confidence,
                "is_rejected": is_rejected,
                "rejection_reason": rejection_reason,
                "model_name": inf_result["model_name"],
                "model_seed": inf_result["seed"],
                "top_k_json": inf_result["candidates"],
                "image_sha256": image_sha256,
                "processing_time_ms": total_processing_time_ms,
                "advisory_id": advisory_id_val,
                "explanation_available": bool(explanation_obj and explanation_obj.explanation_available),
                "calibrated_confidence": calibrated_conf,
            }

            if db is not None:
                saved_record = history_repo.create_prediction(db, record_data, user_id=user_id)
                prediction_id = saved_record.id
            else:
                with get_db_context() as session:
                    saved_record = history_repo.create_prediction(session, record_data, user_id=user_id)
                    prediction_id = saved_record.id

        except Exception as db_err:
            logger.error(f"Failed to persist prediction record to database: {db_err}", exc_info=True)
            # Safe degradation: do not let database write failure crash user response

        return DiagnosisResponse(
            prediction_id=prediction_id,
            user_id=user_id,
            image_sha256=image_sha256,
            processing_time_ms=total_processing_time_ms,
            crop=crop,
            language=language,
            prediction=prediction_result,
            calibration=calibration_info,
            explanation=explanation_obj,
            advisory=advisory_rec,
            knowledge=knowledge_obj,
        )


diagnosis_service = DiagnosisService()
