"""
routes.py - LeafLens REST API Endpoints

Provides:
- Health and model availability status
- Explainable disease diagnosis with automated SQLite persistence
- Multilingual crop advisory queries
- Paginated prediction history retrieval, detail inspection, and cleanup
"""

import json
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status, Depends, Query, Path
from sqlalchemy.orm import Session

from ..models.schemas import (
    CropType,
    Language,
    DiagnosisResponse,
    HealthResponse,
    AdvisoryRecommendation,
    PredictionHistoryItem,
    PredictionHistoryDetail,
    PredictionHistoryList,
    HistoryDeleteResponse,
    HistoryClearResponse,
    CandidateClass,
)
from ..services.diagnosis_service import diagnosis_service
from ..services.inference_service import inference_service
from ..advisory.repository import advisory_repository
from ..auth.dependencies import get_current_user, get_optional_current_user
from ..db.database import get_db
from ..db.models import User
from ..db.repository import history_repo
from ..preprocessing.image_pipeline import ImagePreprocessingError
from ..utils.config import settings
from .auth_routes import auth_router

api_router = APIRouter()

# Mount authentication sub-router (/api/v1/auth)
api_router.include_router(auth_router)


# ===========================================================================
# 1. System Health
# ===========================================================================
@api_router.get("/health", response_model=HealthResponse, tags=["System"])
def check_health(db: Session = Depends(get_db)):
    """Returns system status, active models, resolution, and database connectivity."""
    models_status = {
        "turmeric": inference_service.is_model_available("turmeric"),
        "citrus": inference_service.is_model_available("citrus"),
    }
    model_details = {
        "turmeric": inference_service.get_model_info("turmeric"),
        "citrus": inference_service.get_model_info("citrus"),
    }

    db_status = "connected"
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"

    return HealthResponse(
        status="healthy",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        supported_crops=["turmeric", "citrus"],
        models_available=models_status,
        model_details=model_details,
        database_status=db_status,
    )


# ===========================================================================
# 2. Disease Diagnosis
# ===========================================================================
@api_router.post(
    "/diagnose",
    response_model=DiagnosisResponse,
    tags=["Diagnosis"],
    summary="Perform explainable disease diagnosis on uploaded crop leaf image",
)
async def diagnose_leaf(
    file: UploadFile = File(..., description="Leaf photograph image (JPEG, PNG, WebP)"),
    crop: CropType = Form(..., description="Target crop: turmeric or citrus"),
    language: Language = Form(Language.ENGLISH, description="Advisory language: en, hi, or mr"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Submits a leaf photograph for disease identification:
    - Normalizes image and executes CPU PyTorch inference
    - Computes top-1 prediction, ranked candidate probabilities, and image SHA-256
    - Automatically persists diagnosis telemetry to SQLite database associated with authenticated user
    - Returns prediction and ICAR/KVK vetted treatment recommendations where available
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File must be an image. Received content type: {file.content_type}",
        )

    try:
        image_bytes = await file.read()
        user_id = current_user.id if current_user else None
        response = diagnosis_service.diagnose(
            image_bytes=image_bytes,
            crop=crop,
            language=language,
            db=db,
            user_id=user_id,
        )
        return response

    except ImagePreprocessingError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal diagnosis pipeline error: {str(e)}",
        )


# ===========================================================================
# 3. Advisories
# ===========================================================================
@api_router.get("/advisories/{crop}", response_model=List[AdvisoryRecommendation], tags=["Advisory"])
def list_advisories(crop: CropType, language: Language = Language.ENGLISH):
    """Lists vetted advisories for a given crop."""
    raw_advisories = advisory_repository._cache.get("advisories", [])
    results = []
    for item in raw_advisories:
        if item.get("crop") == crop.value:
            adv = advisory_repository.get_advisory(item.get("disease_id"), crop.value, language.value)
            if adv:
                results.append(adv)
    return results


# ===========================================================================
# 4. Prediction History (User Protected)
# ===========================================================================
@api_router.get(
    "/history",
    response_model=PredictionHistoryList,
    tags=["History"],
    summary="List paginated diagnosis history records for current user",
)
def list_history(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    crop: Optional[CropType] = Query(None, description="Optional crop filter: turmeric or citrus"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves diagnosis history records for the current user, ordered newest first."""
    crop_str = crop.value if crop else None
    records, total_count = history_repo.get_predictions(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        crop=crop_str,
    )

    items = [
        PredictionHistoryItem(
            id=r.id,
            user_id=r.user_id,
            created_at=r.created_at,
            crop=r.crop,
            predicted_class=r.predicted_class,
            confidence=r.confidence,
            is_rejected=r.is_rejected,
            model_name=r.model_name,
            model_seed=r.model_seed,
            image_sha256=r.image_sha256,
            processing_time_ms=r.processing_time_ms,
            explanation_available=r.explanation_available,
        )
        for r in records
    ]

    return PredictionHistoryList(
        total=total_count,
        limit=limit,
        offset=offset,
        items=items,
    )


@api_router.get(
    "/history/{id}",
    response_model=PredictionHistoryDetail,
    tags=["History"],
    summary="Get complete details for a single saved prediction owned by current user",
)
def get_history_detail(
    id: int = Path(..., ge=1, description="Prediction history primary key ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves complete details of a specific diagnosis owned by the authenticated user."""
    record = history_repo.get_prediction_by_id(db=db, prediction_id=id, user_id=current_user.id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction history record with ID {id} not found.",
        )

    # Parse top-k candidate probabilities from JSON
    top_k_candidates = []
    try:
        raw_candidates = json.loads(record.top_k_json)
        if isinstance(raw_candidates, list):
            for c in raw_candidates:
                top_k_candidates.append(
                    CandidateClass(
                        class_name=c.get("class_name", ""),
                        probability=c.get("probability", 0.0),
                        raw_probability=c.get("raw_probability", 0.0),
                        calibrated_probability=c.get("calibrated_probability"),
                    )
                )
    except Exception:
        top_k_candidates = []

    return PredictionHistoryDetail(
        id=record.id,
        user_id=record.user_id,
        created_at=record.created_at,
        crop=record.crop,
        predicted_class=record.predicted_class,
        confidence=record.confidence,
        is_rejected=record.is_rejected,
        rejection_reason=record.rejection_reason,
        model_name=record.model_name,
        model_seed=record.model_seed,
        image_sha256=record.image_sha256,
        processing_time_ms=record.processing_time_ms,
        advisory_id=record.advisory_id,
        explanation_available=record.explanation_available,
        calibrated_confidence=record.calibrated_confidence,
        top_k=top_k_candidates,
    )


@api_router.delete(
    "/history/{id}",
    response_model=HistoryDeleteResponse,
    tags=["History"],
    summary="Delete a single saved prediction record owned by current user",
)
def delete_history_record(
    id: int = Path(..., ge=1, description="Prediction history ID to delete"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes an individual history record by ID belonging to current user."""
    success = history_repo.delete_prediction(db=db, prediction_id=id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction history record with ID {id} not found.",
        )
    return HistoryDeleteResponse(deleted=True, id=id)


@api_router.delete(
    "/history",
    response_model=HistoryClearResponse,
    tags=["History"],
    summary="Clear prediction history records owned by current user",
)
def clear_history(
    crop: Optional[CropType] = Query(None, description="Optional crop filter: delete only records for this crop"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Clears all prediction records belonging to the current user."""
    crop_str = crop.value if crop else None
    deleted_count = history_repo.clear_all_predictions(db=db, user_id=current_user.id, crop=crop_str)
    return HistoryClearResponse(cleared=True, count=deleted_count)
