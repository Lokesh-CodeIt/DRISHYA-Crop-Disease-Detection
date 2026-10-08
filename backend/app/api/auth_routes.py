"""
auth_routes.py - LeafLens / DRISHYA Local Authentication Endpoints

Implements:
- POST /api/v1/auth/register (Safe user creation)
- POST /api/v1/auth/login (Credential verification & HttpOnly cookie issuance)
- GET /api/v1/auth/me (Current user session resolution)
- POST /api/v1/auth/logout (Session invalidation & cookie clearance)
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..auth.security import create_access_token, validate_password_length
from ..db.database import get_db
from ..db.models import User
from ..db.repository import user_repo
from ..models.schemas import (
    AuthMessageResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserPreferencesUpdateRequest,
)
from ..utils.config import settings

logger = logging.getLogger("LeafLens.AuthRoutes")

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new local user",
)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user account:
    - Normalizes email
    - Enforces password validation
    - Hashes password securely via salted bcrypt
    - Never stores plaintext passwords
    - Returns safe public user profile
    """
    # 1. Validate password constraints
    try:
        validate_password_length(req.password)
    except ValueError as pwd_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(pwd_err),
        )

    # 2. Check for duplicate email
    existing_user = user_repo.get_user_by_email(db, req.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )

    # 3. Create user record safely
    try:
        new_user = user_repo.create_user(
            db=db,
            name=req.name,
            email=req.email,
            password=req.password,
            preferred_language=req.preferred_language,
        )
        return new_user
    except Exception as err:
        logger.error(f"User registration error: {err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account. Please try again.",
        )


@auth_router.post(
    "/login",
    response_model=UserResponse,
    summary="Authenticate user and set HttpOnly session cookie",
)
def login(req: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    Authenticates user credentials and issues an HttpOnly session cookie:
    - Verifies password hash using constant-time comparison
    - Issues signed JWT token stored exclusively in an HttpOnly cookie
    - Returns safe user profile (no password hash)
    """
    user = user_repo.authenticate_user(db, req.email, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    # Create signed session token
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    # Set secure HttpOnly session cookie for localhost
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=settings.AUTH_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.AUTH_TOKEN_EXPIRE_MINUTES * 60,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
        path="/",
    )

    logger.info(f"User #{user.id} ({user.email}) successfully logged in.")
    return user


@auth_router.get(
    "/me",
    response_model=UserResponse,
    summary="Get currently authenticated user profile",
)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the authenticated user's safe profile.
    Rejects unauthenticated requests with 401 Unauthorized.
    """
    return current_user


@auth_router.post(
    "/logout",
    response_model=AuthMessageResponse,
    summary="Clear authentication session cookie",
)
def logout(response: Response, current_user: User = Depends(get_current_user)):
    """
    Clears the HttpOnly authentication cookie to terminate the session.
    """
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        path="/",
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
    )
    logger.info(f"User #{current_user.id} logged out successfully.")
    return AuthMessageResponse(message="Successfully logged out.")


@auth_router.patch(
    "/me/preferences",
    response_model=UserResponse,
    summary="Update authenticated user language preference",
)
def update_preferences(
    req: UserPreferencesUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates the authenticated user's preferred language.
    Strictly validates against supported locales (en, hi, mr).
    Updates only the current user's record.
    """
    updated_user = user_repo.update_user_preference(
        db=db,
        user_id=current_user.id,
        preferred_language=req.preferred_language.value,
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found.",
        )
    return updated_user

