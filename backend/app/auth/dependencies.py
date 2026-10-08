"""
dependencies.py - DRISHYA Authentication Dependencies

Provides:
- get_current_user: Strictly requires authenticated session, reads HttpOnly cookie
- get_optional_current_user: Soft authentication for mixed/guest workflows
"""

import logging
from typing import Optional
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .security import decode_access_token
from ..db.database import get_db
from ..db.models import User
from ..db.repository import user_repo
from ..utils.config import settings

logger = logging.getLogger("LeafLens.AuthDependency")


def extract_token_from_request(request: Request) -> Optional[str]:
    """Extracts session token from HttpOnly cookie (primary) or Bearer header (fallback)."""
    # 1. Primary: HttpOnly cookie
    cookie_token = request.cookies.get(settings.AUTH_COOKIE_NAME)
    if cookie_token:
        return cookie_token

    # 2. Secondary fallback: Authorization Header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip()

    return None


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Validates active session and loads current User entity.
    Raises HTTP 401 if unauthenticated or session is invalid/expired.
    """
    token = extract_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed session identity.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    return user


def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Attempts to identify the current user.
    Returns User if valid session exists, None otherwise (does not raise 401).
    """
    token = extract_token_from_request(request)
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None

    try:
        user_id = int(payload["sub"])
        user = user_repo.get_user_by_id(db, user_id)
        if user and user.is_active:
            return user
    except Exception:
        return None

    return None
