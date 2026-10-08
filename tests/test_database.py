"""
test_database.py - Isolated Unit and Integration Tests for SQLite History System

Uses an in-memory SQLite database (sqlite:///:memory:) during test execution
to guarantee zero mutation of production database/leaflens.db.

Validates:
1. Safe database initialization and table schema creation
2. Record creation, retrieval, and fields fidelity
3. Pagination (limit, offset) and sorting (newest first)
4. Crop filtering (turmeric vs citrus)
5. Individual deletion and bulk clearing
6. Automatic prediction recording on POST /api/v1/diagnose
7. API history endpoints: GET /history, GET /history/{id}, DELETE /history/{id}, DELETE /history
"""

import io
import json
import pytest
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import Base, get_db
from backend.app.db.models import PredictionHistory
from backend.app.db.repository import history_repo
from backend.app.services.inference_service import inference_service

# Create isolated in-memory engine with StaticPool so all connections share the same memory DB
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)



@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """Initializes in-memory tables and attaches dependency override."""
    Base.metadata.create_all(bind=test_engine)
    inference_service.initialize_models()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def db_session():
    """Provides a fresh database session for unit tests, cleaning up after."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.query(PredictionHistory).delete()
        session.commit()
        session.close()


def create_sample_leaf_bytes(size=(300, 300), color=(50, 160, 50)) -> bytes:
    """Helper to create dummy image bytes."""
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ===========================================================================
# 1. Database Initialization & Table Creation
# ===========================================================================
def test_database_initialization_and_tables(db_session):
    """Verifies tables are created in SQLite without error."""
    assert test_engine.dialect.has_table(test_engine.connect(), "prediction_history")


# ===========================================================================
# 2. Repository CRUD Operations
# ===========================================================================
def test_create_and_get_prediction_by_id(db_session):
    """Verifies a prediction history record can be inserted and retrieved."""
    sample_data = {
        "crop": "turmeric",
        "predicted_class": "Healthy",
        "confidence": 0.985,
        "is_rejected": False,
        "rejection_reason": None,
        "model_name": "convnext_tiny",
        "model_seed": 42,
        "top_k_json": json.dumps([{"class_name": "Healthy", "probability": 0.985}]),
        "image_sha256": "abc123hash",
        "processing_time_ms": 14.5,
        "advisory_id": None,
        "explanation_available": False,
        "calibrated_confidence": None,
    }

    record = history_repo.create_prediction(db_session, sample_data)
    assert record.id is not None
    assert record.crop == "turmeric"
    assert record.predicted_class == "Healthy"
    assert record.confidence == 0.985
    assert record.image_sha256 == "abc123hash"
    assert record.created_at is not None

    # Fetch by ID
    fetched = history_repo.get_prediction_by_id(db_session, record.id)
    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.predicted_class == "Healthy"


def test_pagination_and_sorting(db_session):
    """Verifies newest-first ordering and limit/offset pagination."""
    for i in range(1, 6):
        history_repo.create_prediction(
            db_session,
            {
                "crop": "citrus",
                "predicted_class": f"Class_{i}",
                "confidence": 0.80 + (i * 0.02),
                "model_name": "efficientnet_v2_s",
                "model_seed": 42,
                "top_k_json": "[]",
                "image_sha256": f"hash_{i}",
                "processing_time_ms": 20.0,
            },
        )

    # First page: 2 items
    page_1, total = history_repo.get_predictions(db_session, limit=2, offset=0)
    assert total == 5
    assert len(page_1) == 2
    assert page_1[0].predicted_class == "Class_5"  # Newest first
    assert page_1[1].predicted_class == "Class_4"

    # Second page: 2 items
    page_2, _ = history_repo.get_predictions(db_session, limit=2, offset=2)
    assert len(page_2) == 2
    assert page_2[0].predicted_class == "Class_3"
    assert page_2[1].predicted_class == "Class_2"


def test_crop_filtering(db_session):
    """Verifies history query filters by crop accurately."""
    # Add 2 turmeric, 3 citrus
    for i in range(2):
        history_repo.create_prediction(
            db_session,
            {
                "crop": "turmeric",
                "predicted_class": "Leaf Spot",
                "confidence": 0.9,
                "model_name": "convnext_tiny",
                "model_seed": 42,
                "top_k_json": "[]",
                "image_sha256": f"turm_{i}",
                "processing_time_ms": 10.0,
            },
        )
    for i in range(3):
        history_repo.create_prediction(
            db_session,
            {
                "crop": "citrus",
                "predicted_class": "Black Spot",
                "confidence": 0.9,
                "model_name": "efficientnet_v2_s",
                "model_seed": 42,
                "top_k_json": "[]",
                "image_sha256": f"citrus_{i}",
                "processing_time_ms": 25.0,
            },
        )

    turm_records, turm_total = history_repo.get_predictions(db_session, crop="turmeric")
    assert turm_total == 2
    assert all(r.crop == "turmeric" for r in turm_records)

    citrus_records, citrus_total = history_repo.get_predictions(db_session, crop="citrus")
    assert citrus_total == 3
    assert all(r.crop == "citrus" for r in citrus_records)


def test_delete_prediction_and_clear_all(db_session):
    """Verifies single deletion and bulk cleanup."""
    rec1 = history_repo.create_prediction(
        db_session,
        {
            "crop": "turmeric",
            "predicted_class": "Dry Leaf",
            "confidence": 0.95,
            "model_name": "convnext_tiny",
            "model_seed": 42,
            "top_k_json": "[]",
            "image_sha256": "h1",
            "processing_time_ms": 10.0,
        },
    )
    rec2 = history_repo.create_prediction(
        db_session,
        {
            "crop": "citrus",
            "predicted_class": "Citrus Canker",
            "confidence": 0.92,
            "model_name": "efficientnet_v2_s",
            "model_seed": 42,
            "top_k_json": "[]",
            "image_sha256": "h2",
            "processing_time_ms": 20.0,
        },
    )

    # Delete 1 record
    assert history_repo.delete_prediction(db_session, rec1.id) is True
    assert history_repo.get_prediction_by_id(db_session, rec1.id) is None
    # Deleting again returns False
    assert history_repo.delete_prediction(db_session, rec1.id) is False

    # Clear remaining
    cleared = history_repo.clear_all_predictions(db_session)
    assert cleared == 1
    assert len(history_repo.get_predictions(db_session)[0]) == 0


# ===========================================================================
# 3. API Integration: Diagnosis -> History Workflow
# ===========================================================================
def test_diagnose_creates_history_record():
    """Verifies POST /api/v1/diagnose automatically persists record to database."""
    client = TestClient(app)
    # Register & login to authenticate for history API
    client.post(
        "/api/v1/auth/register",
        json={"name": "History Tester", "email": "hist_tester@example.com", "password": "Password123!"},
    )
    client.post(
        "/api/v1/auth/login",
        json={"email": "hist_tester@example.com", "password": "Password123!"},
    )

    img_bytes = create_sample_leaf_bytes()

    response = client.post(
        "/api/v1/diagnose",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
        data={"crop": "turmeric", "language": "en"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["prediction_id"] is not None
    assert data["image_sha256"] is not None
    assert len(data["image_sha256"]) == 64
    assert data["processing_time_ms"] > 0

    pred_id = data["prediction_id"]

    # Verify history listing contains this record
    hist_res = client.get("/api/v1/history")
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["total"] >= 1
    assert any(item["id"] == pred_id for item in hist_data["items"])

    # Verify history detail endpoint
    detail_res = client.get(f"/api/v1/history/{pred_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == pred_id
    assert detail["crop"] == "turmeric"
    assert detail["image_sha256"] == data["image_sha256"]
    assert len(detail["top_k"]) == 4

    # Delete the record
    del_res = client.delete(f"/api/v1/history/{pred_id}")
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] is True

    # 404 on deleted record
    assert client.get(f"/api/v1/history/{pred_id}").status_code == 404


def test_history_clear_endpoint():
    """Verifies DELETE /api/v1/history clears all records."""
    client = TestClient(app)
    # Register & login to authenticate for history clear API
    client.post(
        "/api/v1/auth/register",
        json={"name": "Clear Tester", "email": "clear_tester@example.com", "password": "Password123!"},
    )
    client.post(
        "/api/v1/auth/login",
        json={"email": "clear_tester@example.com", "password": "Password123!"},
    )

    img_bytes = create_sample_leaf_bytes()

    # Create 2 diagnoses
    client.post(
        "/api/v1/diagnose",
        files={"file": ("leaf1.jpg", img_bytes, "image/jpeg")},
        data={"crop": "turmeric"},
    )
    client.post(
        "/api/v1/diagnose",
        files={"file": ("leaf2.jpg", img_bytes, "image/jpeg")},
        data={"crop": "citrus"},
    )

    # Clear all
    clear_res = client.delete("/api/v1/history")
    assert clear_res.status_code == 200
    assert clear_res.json()["cleared"] is True
    assert clear_res.json()["count"] >= 2

    # Verify 0 records left
    hist_res = client.get("/api/v1/history")
    assert hist_res.json()["total"] == 0
