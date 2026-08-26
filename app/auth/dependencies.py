from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.guest import GUEST_READ_PERMISSIONS, GUEST_USER, is_guest_request
from app.auth.jwt_handler import decode_access_token
from app.auth.rbac import role_has_permission
from app.auth.user_service import get_user_by_id
from app.core.settings import settings

security = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    user = get_user_by_id(int(payload["sub"]))
    return user


def require_permission(permission: str):
    def dependency(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    ) -> dict:
        if not settings.AUTH_REQUIRED:
            return {"id": 0, "username": "system", "role": "ADMIN", "email": "system@local"}

        if is_guest_request(request):
            if permission in GUEST_READ_PERMISSIONS:
                return dict(GUEST_USER)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {permission}",
            )

        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = decode_access_token(credentials.credentials)
        if not payload or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = get_user_by_id(int(payload["sub"]))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        if not role_has_permission(user["role"], permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {permission}",
            )

        return user

    return dependency
