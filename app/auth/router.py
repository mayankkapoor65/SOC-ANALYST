import logging
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.dependencies import get_current_user_optional, require_permission
from app.auth.guest import GUEST_USER, is_guest_request
from app.auth.jwt_handler import create_access_token
from app.auth.models import TokenResponse, UserLogin, UserRegister, UserResponse
from app.auth.user_service import authenticate_user, count_users, create_user, get_user_by_username
from app.core.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    body: UserRegister,
    current_user: dict = Depends(get_current_user_optional),
):
    """
    Register a new user.
    - First user becomes ADMIN (bootstrap).
    - Subsequent registrations require ADMIN when AUTH_REQUIRED=true.
    """
    if get_user_by_username(body.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    user_count = count_users()
    if user_count == 0:
        role = "ADMIN"
    elif settings.AUTH_REQUIRED:
        if not current_user or current_user.get("role") != "ADMIN":
            raise HTTPException(status_code=403, detail="Only ADMIN can register users")
        role = body.role.upper()
    else:
        role = body.role.upper()

    try:
        user = create_user(body.username, body.email, body.password, role)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except Exception as exc:
        logger.error("Registration failed: %s", exc)
        raise HTTPException(status_code=500, detail="Registration failed")

    return UserResponse(**user)


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin):
    try:
        user = authenticate_user(body.username, body.password)
    except Exception as exc:
        logger.error("Login error: %s", exc)
        raise HTTPException(status_code=500, detail="Authentication service unavailable")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token({"sub": str(user["id"]), "role": user["role"]})
    logger.info("User logged in username=%s role=%s", user["username"], user["role"])
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def me(request: Request, current_user: dict = Depends(get_current_user_optional)):
    if not current_user:
        if is_guest_request(request):
            return UserResponse(
                id=GUEST_USER["id"],
                username=GUEST_USER["username"],
                email=GUEST_USER["email"],
                role=GUEST_USER["role"],
                created_at="",
            )
        if not settings.AUTH_REQUIRED:
            return UserResponse(
                id=0,
                username="guest",
                email="guest@local",
                role="ADMIN",
                created_at="",
            )
        raise HTTPException(status_code=401, detail="Authentication required")
    return UserResponse(**current_user)
