from enum import Enum
from typing import Set


class Role(str, Enum):
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"


# Endpoint permission groups
PERM_DASHBOARD = "dashboard"
PERM_ANALYTICS = "analytics"
PERM_ANOMALIES = "anomalies"
PERM_ALERTS = "alerts"
PERM_INVESTIGATION = "investigation"
PERM_INCIDENT = "incident"
PERM_BASELINES = "baselines"
PERM_ADMIN = "admin"
PERM_INGEST = "ingest"
PERM_THREAT_INTEL = "threat_intel"
PERM_CORRELATION = "correlation"
PERM_ML_EXPLAIN = "ml_explain"


ROLE_PERMISSIONS: dict[Role, Set[str]] = {
    Role.ADMIN: {
        PERM_DASHBOARD,
        PERM_ANALYTICS,
        PERM_ANOMALIES,
        PERM_ALERTS,
        PERM_INVESTIGATION,
        PERM_INCIDENT,
        PERM_BASELINES,
        PERM_ADMIN,
        PERM_INGEST,
        PERM_THREAT_INTEL,
        PERM_CORRELATION,
        PERM_ML_EXPLAIN,
    },
    Role.ANALYST: {
        PERM_DASHBOARD,
        PERM_ANALYTICS,
        PERM_ANOMALIES,
        PERM_ALERTS,
        PERM_INVESTIGATION,
        PERM_INCIDENT,
        PERM_INGEST,
        PERM_THREAT_INTEL,
        PERM_CORRELATION,
        PERM_ML_EXPLAIN,
    },
    Role.VIEWER: {
        PERM_DASHBOARD,
        PERM_ANALYTICS,
        PERM_THREAT_INTEL,
        PERM_CORRELATION,
        PERM_ML_EXPLAIN,
    },
}


def role_has_permission(role: str, permission: str) -> bool:
    try:
        role_enum = Role(role.upper())
    except ValueError:
        return False
    return permission in ROLE_PERMISSIONS.get(role_enum, set())
