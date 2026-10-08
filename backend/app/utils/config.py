"""
Application Configuration settings using Pydantic Settings.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "LeafLens"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    MODELS_DIR: Path = BASE_DIR / "ml" / "models"
    EXPORTED_MODELS_DIR: Path = BASE_DIR / "ml" / "exported_models"
    ADVISORY_FILE: Path = BASE_DIR / "advisory" / "disease_advisories.json"
    DATABASE_PATH: Path = BASE_DIR / "database" / "leaflens.db"

    @property
    def DATABASE_URL(self) -> str:
        # Normalize for SQLite URL with forward slashes
        clean_path = str(self.DATABASE_PATH.resolve()).replace("\\", "/")
        return f"sqlite:///{clean_path}"


    # Inference & Calibration defaults
    UNCERTAINTY_REJECTION_THRESHOLD: float = 0.65
    TURMERIC_TEMPERATURE: float = 1.0
    CITRUS_TEMPERATURE: float = 1.0
    CALIBRATION_ENABLED_BY_CROP: dict[str, bool] = {
        "turmeric": False,
        "citrus": True,
    }

    # Local Authentication & Session Settings
    AUTH_SECRET_KEY: str = "drishya-leaflens-dev-insecure-secret-key-change-in-production-2026"
    AUTH_ALGORITHM: str = "HS256"
    AUTH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    AUTH_COOKIE_NAME: str = "drishya_session"
    AUTH_COOKIE_SECURE: bool = False  # False for plain HTTP localhost development
    AUTH_COOKIE_SAMESITE: str = "lax"


    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
