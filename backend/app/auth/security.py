"""
security.py - DRISHYA Password Hashing and JWT Session Token Utilities

Security Standards:
- Password hashing with bcrypt using salted rounds
- JWT sessions using python-jose HMAC-SHA256
- Constant-time verification
- Safe input boundary validation
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import bcrypt
from jose import jwt, JWTError

from ..utils.config import settings

logger = logging.getLogger("LeafLens.Security")

# Password length constraints
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 128


def validate_password_length(password: str) -> None:
    """Validates that a password satisfies length bounds."""
    if not password or len(password.strip()) == 0:
        raise ValueError("Password cannot be empty.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password must not exceed {MAX_PASSWORD_LENGTH} characters.")


def hash_password(password: str) -> str:
    """Hashes a password with a fresh random salt using bcrypt."""
    validate_password_length(password)
    # bcrypt accepts bytes up to 72 bytes
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a stored bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.warning(f"Password verification error: {e}")
        return False


def create_access_token(
    subject: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Creates a signed JWT access token for user session.
    Accepts subject and/or data dict with extra_claims.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.AUTH_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if data:
        to_encode.update(data)
    if subject is not None:
        to_encode["sub"] = str(subject)
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.AUTH_SECRET_KEY, algorithm=settings.AUTH_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and validates a signed JWT token.
    Returns the payload dictionary if valid, or None if invalid or expired.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.AUTH_SECRET_KEY,
            algorithms=[settings.AUTH_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.debug(f"JWT validation failed: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected token decode error: {e}")
        return None
