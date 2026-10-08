"""
test_localization.py - Unit & Integration Tests for DRISHYA Localization

Validates:
1. English, Hindi, Marathi locales exist, parse cleanly as JSON, and are non-empty
2. Key parity and structure across all three locales
3. Devanagari Unicode script integrity in Hindi & Marathi
4. Dynamic interpolation placeholders consistency ({{name}}, {{count}}, etc.)
5. Dynamic ML condition mapping without altering raw class_to_idx
6. Authenticated user preference update API (PATCH /api/v1/auth/me/preferences)
7. Invalid locale rejection (e.g. 'de', 'fr') with HTTP 422
8. Unauthenticated preference update rejection with HTTP 401
9. User isolation (User A cannot mutate User B's preferred_language)
10. Preference retention after logout
"""

import json
import re
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import Base, get_db
from backend.app.db.models import User
from backend.app.ml.registry import get_active_model_config

LOCALES_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "locales"

# Isolated test DB
TEST_LOC_DB_URL = "sqlite:///:memory:"
loc_test_engine = create_engine(
    TEST_LOC_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
LocTestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=loc_test_engine)


@pytest.fixture(scope="module", autouse=True)
def setup_localization_test_env():
    Base.metadata.create_all(bind=loc_test_engine)

    def override_get_db():
        db = LocTestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=loc_test_engine)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=True)
def clean_loc_tables():
    session = LocTestSessionLocal()
    try:
        session.query(User).delete()
        session.commit()
    finally:
        session.close()


def load_locale(lang_code: str) -> dict:
    file_path = LOCALES_DIR / f"{lang_code}.json"
    assert file_path.exists(), f"Locale file {file_path} not found!"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_keys(d, prefix=""):
    keys = {}
    for k, v in d.items():
        curr_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.update(flatten_keys(v, curr_key))
        else:
            keys[curr_key] = v
    return keys


# ===========================================================================
# 1. Locale Loading & File Integrity
# ===========================================================================
def test_all_locales_exist_and_load():
    """Verifies en.json, hi.json, and mr.json load and parse cleanly."""
    for lang in ["en", "hi", "mr"]:
        data = load_locale(lang)
        assert isinstance(data, dict)
        assert len(data) >= 10, f"Locale {lang} has suspiciously few root keys"


# ===========================================================================
# 2. Key Parity Across Locales
# ===========================================================================
def test_locale_key_parity():
    """Verifies that all core UI keys defined in en.json exist in hi.json and mr.json."""
    en_flat = flatten_keys(load_locale("en"))
    hi_flat = flatten_keys(load_locale("hi"))
    mr_flat = flatten_keys(load_locale("mr"))

    # Core UI keys that must be present in all languages
    core_prefixes = ["app", "nav", "auth", "home", "check", "analysis", "result", "journal", "guide", "about", "privacy", "common", "error", "condition"]

    for key in en_flat:
        prefix = key.split(".")[0]
        if prefix in core_prefixes:
            assert key in hi_flat, f"Missing key in Hindi locale: {key}"
            assert key in mr_flat, f"Missing key in Marathi locale: {key}"


# ===========================================================================
# 3. Devanagari Script Integrity
# ===========================================================================
def test_devanagari_strings_render():
    """Verifies that Hindi and Marathi strings contain authentic Devanagari characters."""
    hi_flat = flatten_keys(load_locale("hi"))
    mr_flat = flatten_keys(load_locale("mr"))

    # Unicode regex for Devanagari range: \u0900-\u097F
    devanagari_pattern = re.compile(r"[\u0900-\u097F]")

    # Verify sample check title
    assert devanagari_pattern.search(hi_flat["check.title"]), "Hindi check.title lacks Devanagari script"
    assert devanagari_pattern.search(mr_flat["check.title"]), "Marathi check.title lacks Devanagari script"

    # Verify sample specific strings from Section R:
    assert hi_flat["check.title"] == "पत्ते की जाँच करें"
    assert mr_flat["check.title"] == "पानाची तपासणी करा"


# ===========================================================================
# 4. Interpolation Tokens Match
# ===========================================================================
def test_dynamic_interpolation_tokens():
    """Verifies placeholders like {{name}} or {{count}} are preserved across locales."""
    en_flat = flatten_keys(load_locale("en"))
    hi_flat = flatten_keys(load_locale("hi"))
    mr_flat = flatten_keys(load_locale("mr"))

    token_pattern = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")

    for key, en_val in en_flat.items():
        if isinstance(en_val, str) and "{{" in en_val:
            en_tokens = set(token_pattern.findall(en_val))
            if en_tokens:
                hi_val = hi_flat.get(key, "")
                mr_val = mr_flat.get(key, "")
                hi_tokens = set(token_pattern.findall(hi_val))
                mr_tokens = set(token_pattern.findall(mr_val))

                assert en_tokens == hi_tokens, f"Token mismatch in Hindi for {key}: expected {en_tokens}, got {hi_tokens}"
                assert en_tokens == mr_tokens, f"Token mismatch in Marathi for {key}: expected {en_tokens}, got {mr_tokens}"


# ===========================================================================
# 5. ML Class Identifiers Unchanged
# ===========================================================================
def test_ml_class_identifiers_remain_intact():
    """Verifies that ML class_to_idx mappings remain 100% unaltered."""
    turmeric_config = get_active_model_config("turmeric")
    citrus_config = get_active_model_config("citrus")

    turmeric_classes = turmeric_config.get_class_to_idx()
    citrus_classes = citrus_config.get_class_to_idx()

    assert len(turmeric_classes) == 4
    assert set(turmeric_classes.keys()) == {"Dry Leaf", "Healthy", "Leaf Blotch", "Leaf Spot"}

    assert len(citrus_classes) == 18
    assert "Citrus Canker" in citrus_classes
    assert "Greening" in citrus_classes
    assert "Healthy" in citrus_classes


# ===========================================================================
# 6. Backend User Preferences API
# ===========================================================================
def test_user_can_update_language_preference():
    """Tests PATCH /api/v1/auth/me/preferences updates user record in SQLite."""
    client = TestClient(app)
    # Register & Login
    client.post(
        "/api/v1/auth/register",
        json={"name": "Kisan Shinde", "email": "kisan@example.com", "password": "Password123!"},
    )
    client.post(
        "/api/v1/auth/login",
        json={"email": "kisan@example.com", "password": "Password123!"},
    )

    # Initial check
    me_res = client.get("/api/v1/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["preferred_language"] == "en"

    # Update to Hindi
    patch_res = client.patch(
        "/api/v1/auth/me/preferences",
        json={"preferred_language": "hi"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["preferred_language"] == "hi"

    # Verify persisted in /auth/me
    verify_res = client.get("/api/v1/auth/me")
    assert verify_res.json()["preferred_language"] == "hi"

    # Update to Marathi
    patch_mr = client.patch(
        "/api/v1/auth/me/preferences",
        json={"preferred_language": "mr"},
    )
    assert patch_mr.status_code == 200
    assert patch_mr.json()["preferred_language"] == "mr"


def test_reject_invalid_language_code():
    """Tests PATCH /api/v1/auth/me/preferences rejects unsupported language with 422."""
    client = TestClient(app)
    client.post(
        "/api/v1/auth/register",
        json={"name": "User Lang", "email": "lang@example.com", "password": "Password123!"},
    )
    client.post(
        "/api/v1/auth/login",
        json={"email": "lang@example.com", "password": "Password123!"},
    )

    # Invalid locale 'fr'
    bad_res = client.patch(
        "/api/v1/auth/me/preferences",
        json={"preferred_language": "fr"},
    )
    assert bad_res.status_code == 422


def test_unauthenticated_preference_update_rejected():
    """Tests PATCH /api/v1/auth/me/preferences rejects guests with 401."""
    client = TestClient(app)
    res = client.patch(
        "/api/v1/auth/me/preferences",
        json={"preferred_language": "hi"},
    )
    assert res.status_code == 401


def test_user_isolation_on_preferences():
    """Verifies User A changing language does NOT affect User B."""
    client_a = TestClient(app)
    client_b = TestClient(app)

    # Setup User A
    client_a.post("/api/v1/auth/register", json={"name": "User A", "email": "a@example.com", "password": "PasswordA123"})
    client_a.post("/api/v1/auth/login", json={"email": "a@example.com", "password": "PasswordA123"})

    # Setup User B
    client_b.post("/api/v1/auth/register", json={"name": "User B", "email": "b@example.com", "password": "PasswordB123"})
    client_b.post("/api/v1/auth/login", json={"email": "b@example.com", "password": "PasswordB123"})

    # User A updates language to 'mr'
    client_a.patch("/api/v1/auth/me/preferences", json={"preferred_language": "mr"})
    assert client_a.get("/api/v1/auth/me").json()["preferred_language"] == "mr"

    # User B's preference must still be 'en'
    assert client_b.get("/api/v1/auth/me").json()["preferred_language"] == "en"


def test_logout_preserves_language_preference_in_db():
    """Verifies preferred_language remains safely stored in DB across sessions."""
    client = TestClient(app)
    client.post("/api/v1/auth/register", json={"name": "Persistent User", "email": "persist@example.com", "password": "Password123!"})
    client.post("/api/v1/auth/login", json={"email": "persist@example.com", "password": "Password123!"})

    # Set to Marathi
    client.patch("/api/v1/auth/me/preferences", json={"preferred_language": "mr"})

    # Logout
    logout_res = client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200

    # Query DB directly to verify persistence
    session = LocTestSessionLocal()
    try:
        user = session.query(User).filter(User.email == "persist@example.com").first()
        assert user is not None
        assert user.preferred_language == "mr"
    finally:
        session.close()
