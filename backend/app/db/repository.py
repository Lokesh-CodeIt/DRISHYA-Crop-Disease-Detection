"""
repository.py - LeafLens / DRISHYA Database Repositories

Encapsulates data access and transaction logic for:
1. User Accounts (Registration, authentication lookup, normalization)
2. Prediction History (User-scoped CRUD, paginated browsing, filtering)
"""

import json
import logging
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import User, PredictionHistory

logger = logging.getLogger("LeafLens.Repository")


class UserRepository:
    """Data access layer for User entities."""

    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalizes email address consistently."""
        if not email:
            return ""
        return email.strip().lower()

    @classmethod
    def create_user(
        cls,
        db: Session,
        name: str,
        email: str,
        password_hash: Optional[str] = None,
        password: Optional[str] = None,
        preferred_language: Optional[str] = "en",
    ) -> User:
        """Creates and persists a new User."""
        clean_email = cls.normalize_email(email)
        if not password_hash and password:
            from ..auth.security import hash_password
            password_hash = hash_password(password)
        if not password_hash:
            raise ValueError("Either password or password_hash must be provided.")

        user = User(
            name=name.strip(),
            email=clean_email,
            password_hash=password_hash,
            preferred_language=preferred_language or "en",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Registered new user #{user.id} ({user.email})")
        return user

    @classmethod
    def get_user_by_id(cls, db: Session, user_id: int) -> Optional[User]:
        """Looks up a user by primary key ID."""
        return db.query(User).filter(User.id == user_id).first()

    @classmethod
    def get_user_by_email(cls, db: Session, email: str) -> Optional[User]:
        """Looks up a user by unique normalized email."""
        clean_email = cls.normalize_email(email)
        return db.query(User).filter(User.email == clean_email).first()

    @classmethod
    def authenticate_user(cls, db: Session, email: str, password: str) -> Optional[User]:
        """Verifies credentials and returns User if valid, else None."""
        from ..auth.security import verify_password
        user = cls.get_user_by_email(db, email)
        if not user or not user.password_hash:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @classmethod
    def update_user_preference(cls, db: Session, user_id: int, preferred_language: str) -> Optional[User]:
        """Updates an authenticated user's preferred language."""
        user = cls.get_user_by_id(db, user_id)
        if not user:
            return None
        user.preferred_language = preferred_language.lower().strip()
        db.commit()
        db.refresh(user)
        logger.info(f"Updated user #{user.id} preferred_language to '{user.preferred_language}'")
        return user


class PredictionHistoryRepository:
    """Data access layer for PredictionHistory records with user ownership."""

    @staticmethod
    def create_prediction(
        db: Session,
        record_data: Dict[str, Any],
        user_id: Optional[int] = None,
    ) -> PredictionHistory:
        """Creates and commits a new prediction history record linked to user_id."""
        # Ensure top_k_json is serialized string
        top_k = record_data.get("top_k_json", "[]")
        if not isinstance(top_k, str):
            top_k = json.dumps(top_k)

        # Allow user_id from parameter or record_data
        effective_user_id = user_id if user_id is not None else record_data.get("user_id")

        prediction = PredictionHistory(
            user_id=effective_user_id,
            crop=record_data["crop"],
            predicted_class=record_data["predicted_class"],
            confidence=record_data["confidence"],
            is_rejected=record_data.get("is_rejected", False),
            rejection_reason=record_data.get("rejection_reason"),
            model_name=record_data["model_name"],
            model_seed=record_data["model_seed"],
            top_k_json=top_k,
            image_sha256=record_data["image_sha256"],
            processing_time_ms=record_data["processing_time_ms"],
            advisory_id=record_data.get("advisory_id"),
            explanation_available=record_data.get("explanation_available", False),
            calibrated_confidence=record_data.get("calibrated_confidence"),
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        logger.info(
            f"Saved prediction #{prediction.id} for user={prediction.user_id} | "
            f"crop='{prediction.crop}' | class='{prediction.predicted_class}'"
        )
        return prediction

    @staticmethod
    def get_predictions(
        db: Session,
        user_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
        crop: Optional[str] = None,
    ) -> Tuple[List[PredictionHistory], int]:
        """
        Retrieves paginated list of predictions ordered newest first.
        Strictly enforces user isolation when user_id is provided.
        Returns: (records, total_count)
        """
        query = db.query(PredictionHistory)

        if user_id is not None:
            query = query.filter(PredictionHistory.user_id == user_id)

        if crop:
            crop_clean = crop.lower().strip()
            query = query.filter(PredictionHistory.crop == crop_clean)

        total_count = query.count()
        records = (
            query.order_by(desc(PredictionHistory.created_at), desc(PredictionHistory.id))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return records, total_count

    @staticmethod
    def get_prediction_by_id(
        db: Session,
        prediction_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[PredictionHistory]:
        """
        Retrieves a single prediction by ID.
        If user_id is given, returns the record ONLY if owned by that user.
        """
        query = db.query(PredictionHistory).filter(PredictionHistory.id == prediction_id)
        if user_id is not None:
            query = query.filter(PredictionHistory.user_id == user_id)
        return query.first()

    @staticmethod
    def delete_prediction(
        db: Session,
        prediction_id: int,
        user_id: Optional[int] = None,
    ) -> bool:
        """
        Deletes a single prediction by ID.
        Guarantees that user_id can only delete their own records.
        Returns True if deleted, False if not found or unauthorized.
        """
        query = db.query(PredictionHistory).filter(PredictionHistory.id == prediction_id)
        if user_id is not None:
            query = query.filter(PredictionHistory.user_id == user_id)

        record = query.first()
        if not record:
            return False

        db.delete(record)
        db.commit()
        logger.info(f"Deleted prediction #{prediction_id} (user={user_id})")
        return True

    @staticmethod
    def clear_all_predictions(
        db: Session,
        user_id: Optional[int] = None,
        crop: Optional[str] = None,
    ) -> int:
        """
        Clears prediction records.
        Strictly scopes deletion to user_id when provided.
        """
        query = db.query(PredictionHistory)
        if user_id is not None:
            query = query.filter(PredictionHistory.user_id == user_id)

        if crop:
            crop_clean = crop.lower().strip()
            query = query.filter(PredictionHistory.crop == crop_clean)

        count = query.delete(synchronize_session=False)
        db.commit()
        logger.info(f"Cleared {count} prediction records (user={user_id}, crop={crop})")
        return count


user_repo = UserRepository()
history_repo = PredictionHistoryRepository()
