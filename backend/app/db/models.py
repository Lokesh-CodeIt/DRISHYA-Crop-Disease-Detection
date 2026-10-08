"""
models.py - LeafLens / DRISHYA SQLAlchemy Database Models

Defines persistence schema for:
1. User Accounts (Local authentication, salted password hashes, UTC timestamps)
2. Prediction/Diagnosis History (Scoped to user_id, telemetry, model attribution)
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from .database import Base


def utc_now():
    """Returns timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class User(Base):
    """User account entity for DRISHYA authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    preferred_language = Column(String(10), nullable=True, default="en")

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    predictions = relationship(
        "PredictionHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(PredictionHistory.created_at)",
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"


class PredictionHistory(Base):
    """Stores records of completed crop disease diagnoses, owned by a user."""

    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # User Ownership
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    user = relationship("User", back_populates="predictions")

    # Crop & Prediction Core
    crop = Column(String(32), nullable=False, index=True)
    predicted_class = Column(String(64), nullable=False)
    confidence = Column(Float, nullable=False)

    # Uncertainty & Rejection
    is_rejected = Column(Boolean, default=False, nullable=False)
    rejection_reason = Column(Text, nullable=True)

    # Model Provenance
    model_name = Column(String(64), nullable=False)
    model_seed = Column(Integer, nullable=False)
    top_k_json = Column(Text, nullable=False)  # JSON-encoded array of candidate class probabilities

    # Audit & Telemetry
    image_sha256 = Column(String(64), nullable=False, index=True)
    processing_time_ms = Column(Float, nullable=False)

    # Integration Placeholders
    advisory_id = Column(String(128), nullable=True)  # Nullable: populated in advisory phase
    explanation_available = Column(Boolean, default=False, nullable=False)
    calibrated_confidence = Column(Float, nullable=True)  # Nullable: populated in calibration phase

    __table_args__ = (
        Index("ix_prediction_user_created", "user_id", "created_at"),
        Index("ix_prediction_crop_created", "crop", "created_at"),
    )

    def __repr__(self):
        return f"<PredictionHistory(id={self.id}, user_id={self.user_id}, crop='{self.crop}', class='{self.predicted_class}')>"
