"""
test_auth.py - Comprehensive Unit and Integration Tests for DRISHYA Local Authentication

Tests:
1. Register user
2. Duplicate email rejected
3. Password is hashed and not stored plaintext
4. Login succeeds with valid credentials (HttpOnly cookie set)
5. Login fails with invalid credentials
6. /auth/me works for authenticated user
7. /auth/me rejects unauthenticated request (401)
8. Logout clears session and invalidates access
9. Authenticated user can access own history
10. User A cannot access User B's history (isolation across GET, detail, and DELETE)
11. Diagnosis stores authenticated user_id
12. Health endpoint remains accessible without authentication
"""

import io
import pytest
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import Base, get_db
from backend.app.db.models import User, PredictionHistory
from backend.app.auth.security import verify_password
from backend.app.services.inference_service import inference_service
from backend.app.utils.config import settings

# Isolated in-memory SQLite database
TEST_AUTH_DB_URL = "sqlite:///:memory:"
auth_test_engine = create_engine(
    TEST_AUTH_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
AuthTestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=auth_test_engine)


@pytest.fixture(scope="module", autouse=True)
def setup_auth_test_environment():
    """Initializes in-memory tables and attaches dependency override."""
    Base.metadata.create_all(bind=auth_test_engine)
    inference_service.initialize_models()

    def override_get_db():
        db = AuthTestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=auth_test_engine)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=True)
def clear_auth_db():
    """Wipes test tables between tests to ensure test isolation."""
    session = AuthTestSessionLocal()
    try:
        session.query(PredictionHistory).delete()
        session.query(User).delete()
        session.commit()
    finally:
        session.close()


def create_sample_leaf_bytes(size=(300, 300), color=(50, 160, 50)) -> bytes:
    """Helper to create dummy JPEG image bytes."""
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ===========================================================================
# 1. Register User
# ===========================================================================
def test_register_user_success():
    client = TestClient(app)
    res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Ramesh Kumar",
            "email": "ramesh@example.com",
            "password": "SecurePassword123!",
            "preferred_language": "mr",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["id"] is not None
    assert data["name"] == "Ramesh Kumar"
    assert data["email"] == "ramesh@example.com"
    assert data["preferred_language"] == "mr"
    assert data["is_active"] is True
    # Ensure password and hash are NEVER returned
    assert "password" not in data
    assert "password_hash" not in data


# ===========================================================================
# 2. Duplicate Email Rejected
# ===========================================================================
def test_duplicate_email_rejected():
    client = TestClient(app)
    payload = {
        "name": "Suresh Patel",
        "email": "suresh@example.com",
        "password": "Password123!",
    }
    first_res = client.post("/api/v1/auth/register", json=payload)
    assert first_res.status_code == 201

    # Second attempt with same email
    dup_res = client.post("/api/v1/auth/register", json=payload)
    assert dup_res.status_code == 409
    assert "already exists" in dup_res.json()["detail"].lower()


# ===========================================================================
# 3. Password Hashed and Not Stored Plaintext
# ===========================================================================
def test_password_is_hashed_and_not_plaintext():
    client = TestClient(app)
    raw_pwd = "MySecretPassword99"
    res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Anil Verma",
            "email": "anil@example.com",
            "password": raw_pwd,
        },
    )
    assert res.status_code == 201

    session = AuthTestSessionLocal()
    try:
        user = session.query(User).filter(User.email == "anil@example.com").first()
        assert user is not None
        assert user.password_hash != raw_pwd
        assert user.password_hash.startswith("$2b$") or user.password_hash.startswith("$2a$")
        assert verify_password(raw_pwd, user.password_hash) is True
        assert verify_password("wrongpassword", user.password_hash) is False
    finally:
        session.close()


# ===========================================================================
# 4. Login Succeeds with Valid Credentials & Sets HttpOnly Cookie
# ===========================================================================
def test_login_succeeds_with_valid_credentials():
    client = TestClient(app)
    # Register
    client.post(
        "/api/v1/auth/register",
        json={"name": "Kavita Rao", "email": "kavita@example.com", "password": "PassWord123"},
    )

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "kavita@example.com", "password": "PassWord123"},
    )
    assert login_res.status_code == 200
    user_data = login_res.json()
    assert user_data["email"] == "kavita@example.com"
    assert "password_hash" not in user_data

    # Verify HttpOnly Cookie is set
    assert settings.AUTH_COOKIE_NAME in login_res.cookies
    token_val = login_res.cookies[settings.AUTH_COOKIE_NAME]
    assert token_val is not None and len(token_val) > 20


# ===========================================================================
# 5. Login Fails with Invalid Credentials
# ===========================================================================
def test_login_fails_with_invalid_credentials():
    client = TestClient(app)
    client.post(
        "/api/v1/auth/register",
        json={"name": "Sunil Shinde", "email": "sunil@example.com", "password": "ValidPassword123"},
    )

    # Wrong password
    bad_pwd_res = client.post(
        "/api/v1/auth/login",
        json={"email": "sunil@example.com", "password": "WrongPassword!"},
    )
    assert bad_pwd_res.status_code == 401
    assert "invalid" in bad_pwd_res.json()["detail"].lower()

    # Nonexistent user
    bad_email_res = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "AnyPassword"},
    )
    assert bad_email_res.status_code == 401


# ===========================================================================
# 6. /auth/me Works for Authenticated User
# ===========================================================================
def test_auth_me_authenticated():
    client = TestClient(app)
    client.post(
        "/api/v1/auth/register",
        json={"name": "Pooja Patil", "email": "pooja@example.com", "password": "PoojaPassword123"},
    )
    client.post(
        "/api/v1/auth/login",
        json={"email": "pooja@example.com", "password": "PoojaPassword123"},
    )

    me_res = client.get("/api/v1/auth/me")
    assert me_res.status_code == 200
    data = me_res.json()
    assert data["name"] == "Pooja Patil"
    assert data["email"] == "pooja@example.com"
    assert "password_hash" not in data


# ===========================================================================
# 7. /auth/me Rejects Unauthenticated Request
# ===========================================================================
def test_auth_me_unauthenticated_rejected():
    client = TestClient(app)
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
    assert "authentication required" in res.json()["detail"].lower() or "unauthorized" in res.json()["detail"].lower()


# ===========================================================================
# 8. Logout Clears Session
# ===========================================================================
def test_logout_clears_session():
    client = TestClient(app)
    client.post(
        "/api/v1/auth/register",
        json={"name": "Ganesh G", "email": "ganesh@example.com", "password": "PasswordGanesh123"},
    )
    client.post(
        "/api/v1/auth/login",
        json={"email": "ganesh@example.com", "password": "PasswordGanesh123"},
    )

    # Verify authenticated
    assert client.get("/api/v1/auth/me").status_code == 200

    # Logout
    logout_res = client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Successfully logged out."

    # Subsequent /auth/me call fails with 401
    assert client.get("/api/v1/auth/me").status_code == 401


# ===========================================================================
# 9. Authenticated User Can Access Own History
# ===========================================================================
def test_authenticated_user_can_access_own_history():
    client = TestClient(app)
    client.post(
        "/api/v1/auth/register",
        json={"name": "User One", "email": "user1@example.com", "password": "Password12345"},
    )
    client.post(
        "/api/v1/auth/login",
        json={"email": "user1@example.com", "password": "Password12345"},
    )

    # Perform diagnosis while authenticated
    img_bytes = create_sample_leaf_bytes()
    diag_res = client.post(
        "/api/v1/diagnose",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
        data={"crop": "turmeric"},
    )
    assert diag_res.status_code == 200
    pred_id = diag_res.json()["prediction_id"]

    # History list
    hist_res = client.get("/api/v1/history")
    assert hist_res.status_code == 200
    hist_items = hist_res.json()["items"]
    assert len(hist_items) == 1
    assert hist_items[0]["id"] == pred_id


# ===========================================================================
# 10. User A Cannot Access User B's History (Strict Isolation)
# ===========================================================================
def test_user_a_cannot_access_user_b_history():
    # 1. Setup User A
    client_a = TestClient(app)
    client_a.post(
        "/api/v1/auth/register",
        json={"name": "Farmer A", "email": "farmer_a@example.com", "password": "PasswordA123"},
    )
    client_a.post(
        "/api/v1/auth/login",
        json={"email": "farmer_a@example.com", "password": "PasswordA123"},
    )

    img_bytes = create_sample_leaf_bytes()
    diag_res_a = client_a.post(
        "/api/v1/diagnose",
        files={"file": ("leaf_a.jpg", img_bytes, "image/jpeg")},
        data={"crop": "turmeric"},
    )
    assert diag_res_a.status_code == 200
    pred_id_a = diag_res_a.json()["prediction_id"]

    # 2. Setup User B
    client_b = TestClient(app)
    client_b.post(
        "/api/v1/auth/register",
        json={"name": "Farmer B", "email": "farmer_b@example.com", "password": "PasswordB123"},
    )
    client_b.post(
        "/api/v1/auth/login",
        json={"email": "farmer_b@example.com", "password": "PasswordB123"},
    )

    # 3. User B lists history -> should see 0 records
    hist_res_b = client_b.get("/api/v1/history")
    assert hist_res_b.status_code == 200
    assert hist_res_b.json()["total"] == 0
    assert len(hist_res_b.json()["items"]) == 0

    # 4. User B attempts to access User A's record directly by ID -> 404
    detail_res_b = client_b.get(f"/api/v1/history/{pred_id_a}")
    assert detail_res_b.status_code == 404

    # 5. User B attempts to delete User A's record directly -> 404
    del_res_b = client_b.delete(f"/api/v1/history/{pred_id_a}")
    assert del_res_b.status_code == 404

    # 6. User B calls clear_history -> clears 0, User A's record still exists
    clear_res_b = client_b.delete("/api/v1/history")
    assert clear_res_b.status_code == 200
    assert clear_res_b.json()["count"] == 0

    # Verify User A's record is still intact
    detail_res_a = client_a.get(f"/api/v1/history/{pred_id_a}")
    assert detail_res_a.status_code == 200
    assert detail_res_a.json()["id"] == pred_id_a


# ===========================================================================
# 11. Diagnosis Stores the Authenticated user_id
# ===========================================================================
def test_diagnosis_stores_authenticated_user_id():
    client = TestClient(app)
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"name": "Diagnostic Farmer", "email": "diag@example.com", "password": "PasswordDiag123"},
    )
    user_id = reg_res.json()["id"]
    client.post(
        "/api/v1/auth/login",
        json={"email": "diag@example.com", "password": "PasswordDiag123"},
    )

    img_bytes = create_sample_leaf_bytes()
    diag_res = client.post(
        "/api/v1/diagnose",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
        data={"crop": "citrus"},
    )
    assert diag_res.status_code == 200
    diag_data = diag_res.json()
    assert diag_data["user_id"] == user_id

    # Verify in DB
    session = AuthTestSessionLocal()
    try:
        record = session.query(PredictionHistory).filter(PredictionHistory.id == diag_data["prediction_id"]).first()
        assert record is not None
        assert record.user_id == user_id
    finally:
        session.close()


# ===========================================================================
# 12. Health Endpoint Remains Accessible Without Authentication
# ===========================================================================
def test_health_endpoint_remains_unprotected():
    client = TestClient(app)
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
