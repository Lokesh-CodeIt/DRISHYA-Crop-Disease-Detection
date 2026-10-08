"""
database.py - LeafLens SQLite Database Engine & Session Management

Provides:
- Non-destructive database initialization (init_db)
- Safe schema migration for user_id foreign key
- FastAPI session dependency (get_db)
- Context manager for background/service session handling
"""

import logging
from pathlib import Path
from typing import Generator, Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from ..utils.config import settings

logger = logging.getLogger("LeafLens.Database")

Base = declarative_base()

# Global engine and session factory
_engine = None
_SessionFactory = None


def ensure_schema_migrations(engine):
    """
    Safely applies non-destructive incremental schema updates,
    preserving existing rows in prediction_history while linking user ownership.
    """
    try:
        inspector = inspect(engine)
        if inspector.has_table("prediction_history"):
            columns = [c["name"] for c in inspector.get_columns("prediction_history")]
            if "user_id" not in columns:
                logger.info("Applying non-destructive migration: Adding user_id to prediction_history...")
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE prediction_history ADD COLUMN user_id INTEGER REFERENCES users(id);"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_prediction_user_created ON prediction_history(user_id, created_at);"))
                    conn.commit()
                logger.info("Migration complete: user_id column added successfully.")
    except Exception as e:
        logger.warning(f"Schema migration check encountered non-fatal note: {e}")


def get_engine(database_url: Optional[str] = None):
    """Returns or creates the SQLAlchemy engine."""
    global _engine, _SessionFactory
    if _engine is None or database_url is not None:
        url = database_url or settings.DATABASE_URL

        # Ensure parent directory exists for SQLite
        if url.startswith("sqlite:///"):
            raw_path = url.replace("sqlite:///", "")
            db_file = Path(raw_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)

        engine = create_engine(
            url,
            connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
            echo=False,
            future=True,
        )

        session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            future=True,
        )

        # Import models and ensure tables exist
        from . import models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        ensure_schema_migrations(engine)

        if database_url is None:
            _engine = engine
            _SessionFactory = session_factory
            return _engine
        return engine

    return _engine


def get_session_factory():
    """Returns the default SessionLocal factory."""
    global _SessionFactory
    if _SessionFactory is None:
        get_engine()
    return _SessionFactory


def init_db(database_url: Optional[str] = None):
    """
    Initializes database schema safely without dropping or altering existing data.
    Creates tables if they do not already exist, and migrates schema cleanly.
    """
    engine = get_engine(database_url)
    from . import models  # noqa: F401

    logger.info("Initializing LeafLens SQLite database tables...")
    Base.metadata.create_all(bind=engine)
    ensure_schema_migrations(engine)
    logger.info("LeafLens database initialized successfully.")


def get_db() -> Generator[Session, None, None]:
    """FastAPI route dependency yielding a database session."""
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for standalone service usage."""
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()
