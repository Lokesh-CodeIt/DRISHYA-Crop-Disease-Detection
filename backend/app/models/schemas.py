"""
Pydantic Request and Response schemas for LeafLens / DRISHYA API.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class CropType(str, Enum):
    TURMERIC = "turmeric"
    CITRUS = "citrus"


class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    MARATHI = "mr"


# ===========================================================================
# Authentication Schemas
# ===========================================================================
class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User full name")
    email: str = Field(..., min_length=3, max_length=255, description="User email address")
    password: str = Field(..., min_length=6, max_length=128, description="User password")
    preferred_language: Optional[str] = Field(default="en", max_length=10, description="Preferred language code (en, hi, mr)")


class UserLoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255, description="Registered email address")
    password: str = Field(..., min_length=1, max_length=128, description="User password")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    preferred_language: Optional[str] = "en"
    created_at: datetime
    is_active: bool


class UserPreferencesUpdateRequest(BaseModel):
    preferred_language: Language = Field(..., description="Preferred language code: en, hi, or mr")


class AuthMessageResponse(BaseModel):
    message: str


# ===========================================================================
# Prediction & Diagnosis Schemas
# ===========================================================================
class CandidateClass(BaseModel):
    class_name: str
    probability: float = Field(default=0.0, description="Predicted class probability")
    raw_probability: float = Field(default=0.0, description="Raw uncalibrated softmax probability")
    calibrated_probability: Optional[float] = Field(default=None, description="Calibrated probability once calibration is active")


class CalibrationInfo(BaseModel):
    temperature_applied: Optional[float] = Field(default=None, description="Temperature scaling factor T, if applied")
    raw_confidence: float = Field(..., description="Raw top-1 softmax probability")
    calibrated_confidence: Optional[float] = Field(default=None, description="Calibrated top-1 probability")
    is_active: bool = Field(default=False, description="Whether post-hoc calibration was applied")
    is_uncertain: bool = Field(default=False, description="Whether confidence falls below rejection safety threshold")
    rejection_threshold: float = Field(default=0.65, description="Uncertainty threshold")


class AttentionRegion(BaseModel):
    region_id: int = Field(..., description="1-indexed rank of attention region")
    x: int = Field(..., description="Top-left x pixel coordinate on original image")
    y: int = Field(..., description="Top-left y pixel coordinate on original image")
    width: int = Field(..., description="Bounding box width in pixels")
    height: int = Field(..., description="Bounding box height in pixels")
    attention_score: float = Field(..., description="Normalized mean attention score within region [0.0, 1.0]")
    crop_base64: str = Field(..., description="Base64 encoded JPEG thumbnail cropped from original image")


class GradCAMExplanation(BaseModel):
    method: str = Field(default="Grad-CAM", description="Explainability method")
    target_class: str = Field(..., description="Predicted class name explained")
    target_layer: Optional[str] = Field(default=None, description="Feature layer tapped")
    overlay_base64: Optional[str] = Field(default=None, description="Base64 encoded PNG overlay on original image")
    image_width: int = Field(..., description="Original image width in pixels")
    image_height: int = Field(..., description="Original image height in pixels")
    regions: List[AttentionRegion] = Field(default_factory=list, description="Top spatially distinct attention regions (max 3)")
    processing_time_ms: float = Field(default=0.0, description="Explanation latency in milliseconds")
    explanation_available: bool = Field(default=True, description="True if valid explanation generated")
    reason: Optional[str] = Field(default=None, description="Internal diagnostic reason if explanation or regions are unavailable")
    
    # Backward compatibility fields
    mean_intensity: Optional[float] = None
    high_attention_area_fraction: Optional[float] = None
    focus_score: Optional[float] = None


class TreatmentSource(BaseModel):
    institution: str
    document_title: str
    url_or_reference: Optional[str] = None


class KnowledgeSource(BaseModel):
    source_title: str
    source_organization: str
    source_url: Optional[str] = None
    source_type: str = "institutional_extension"


class ConditionKnowledge(BaseModel):
    condition_id: str
    crop: str
    display_name: str
    short_description: str
    what_it_means: str
    visual_signs: List[str] = []
    immediate_actions: List[str] = []
    prevention_or_monitoring: List[str] = []
    expert_escalation: str
    advisory_status: str = "SUPPORTED"  # "SUPPORTED", "GENERAL_GUIDANCE", "EXPERT_CONFIRMATION_RECOMMENDED"
    sources: List[KnowledgeSource] = []
    reference_image: Optional[str] = None
    knowledge_available: bool = True


class AdvisoryRecommendation(BaseModel):
    disease_id: str
    crop: str
    scientific_name: Optional[str] = None
    common_name: Optional[str] = None
    symptoms: Optional[str] = None
    cultural_preventative_measures: List[str] = []
    organic_biological_controls: List[str] = []
    chemical_controls: List[str] = []
    safety_warnings: Optional[str] = None
    authoritative_sources: List[TreatmentSource] = []


class PredictionResult(BaseModel):
    predicted_class: str
    confidence: float = Field(..., description="Top-1 inference confidence")
    calibrated_confidence: Optional[float] = Field(default=None, description="Calibrated confidence when calibration is active")
    is_rejected: bool = Field(default=False, description="Flagged if rejected due to high uncertainty")
    rejection_reason: Optional[str] = None
    candidates: List[CandidateClass] = []


class DiagnosisResponse(BaseModel):
    prediction_id: Optional[int] = Field(default=None, description="Saved database history record ID")
    user_id: Optional[int] = Field(default=None, description="Owner user ID if authenticated")
    image_sha256: Optional[str] = Field(default=None, description="SHA-256 fingerprint of uploaded image")
    processing_time_ms: Optional[float] = Field(default=None, description="Inference and preprocessing elapsed time in milliseconds")
    crop: CropType
    language: Language = Language.ENGLISH
    prediction: PredictionResult
    calibration: CalibrationInfo
    explanation: Optional[GradCAMExplanation] = None
    advisory: Optional[AdvisoryRecommendation] = None
    knowledge: Optional[ConditionKnowledge] = None


# ===========================================================================
# History Schemas
# ===========================================================================
class PredictionHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    created_at: datetime
    crop: str
    predicted_class: str
    confidence: float
    is_rejected: bool
    model_name: str
    model_seed: int
    image_sha256: str
    processing_time_ms: float
    explanation_available: bool


class PredictionHistoryDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    created_at: datetime
    crop: str
    predicted_class: str
    confidence: float
    is_rejected: bool
    rejection_reason: Optional[str] = None
    model_name: str
    model_seed: int
    image_sha256: str
    processing_time_ms: float
    advisory_id: Optional[str] = None
    explanation_available: bool
    calibrated_confidence: Optional[float] = None
    top_k: List[CandidateClass] = []


class PredictionHistoryList(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[PredictionHistoryItem]


class HistoryDeleteResponse(BaseModel):
    deleted: bool
    id: int
    message: str = "Record deleted successfully"


class HistoryClearResponse(BaseModel):
    cleared: bool
    count: int
    message: str = "History cleared successfully"


# ===========================================================================
# System Health Schemas
# ===========================================================================
class HealthResponse(BaseModel):
    status: str = "healthy"
    project: str = "LeafLens"
    version: str
    supported_crops: List[str]
    models_available: Dict[str, bool]
    model_details: Optional[Dict[str, Any]] = None
    database_status: Optional[str] = "connected"
