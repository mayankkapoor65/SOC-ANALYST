"""Demo guest session helpers (Phase 12.2)."""

from app.auth.rbac import (
    PERM_ANALYTICS,
    PERM_CORRELATION,
    PERM_DASHBOARD,
    PERM_ML_EXPLAIN,
    PERM_THREAT_INTEL,
)

GUEST_USER = {
    "id": 0,
    "username": "guest",
    "email": "guest@local",
    "role": "VIEWER",
}

GUEST_HEADER = "x-sentinel-guest"

GUEST_READ_PERMISSIONS = {
    PERM_DASHBOARD,
    PERM_ANALYTICS,
    PERM_THREAT_INTEL,
    PERM_CORRELATION,
    PERM_ML_EXPLAIN,
}


def is_guest_request(request) -> bool:
    value = (request.headers.get(GUEST_HEADER) or "").strip().lower()
    return value in ("1", "true", "yes")
