# Phase 12 — SOC Platform Features

**Version:** 1.0  
**Date:** 2026-08-13  
**Scope:** Enterprise SOC monitoring — authentication, RBAC, MITRE ATT&CK, investigation workflows, incident reporting, Docker deployment

---

## Overview

Phase 12 transforms SentinelAI from a detection demo into an enterprise-grade SOC analyst platform suitable for cybersecurity portfolios, internships, and analyst role applications — while preserving all Phase 11 detection logic and API backward compatibility.

---

## JWT Authentication Architecture

### Components

| Module | Purpose |
|--------|---------|
| `app/auth/jwt_handler.py` | Token creation and validation (python-jose) |
| `app/auth/password.py` | bcrypt password hashing |
| `app/auth/user_service.py` | User CRUD and authentication |
| `app/auth/dependencies.py` | FastAPI `Depends()` guards |
| `app/auth/router.py` | `/login`, `/register`, `/me` routes |

### Token Flow

```
1. Client POST /login { username, password }
2. Server validates credentials against users table
3. Server returns { access_token, token_type: "bearer" }
4. Client sends Authorization: Bearer <token> on protected routes
5. Server validates JWT signature + expiry, extracts role
```

### Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | (dev default) | HMAC signing key — **change in production** |
| `JWT_ALGORITHM` | HS256 | Signing algorithm |
| `JWT_EXPIRE_MINUTES` | 60 | Token lifetime |
| `AUTH_REQUIRED` | false | Enable RBAC enforcement |
| `DEFAULT_ADMIN_USERNAME` | admin | Bootstrap admin username |
| `DEFAULT_ADMIN_PASSWORD` | Admin123! | Bootstrap admin password |

### Bootstrap Behavior

On first startup with an empty `users` table, a default ADMIN account is seeded automatically using `DEFAULT_ADMIN_*` environment variables.

The first user registered via `POST /register` also receives ADMIN role if no users exist.

---

## RBAC Model

### Roles

| Role | Description |
|------|-------------|
| **ADMIN** | Full platform access, user registration, baselines |
| **ANALYST** | SOC investigation — alerts, anomalies, analytics, reports |
| **VIEWER** | Read-only dashboard monitoring |

### Permission Matrix

| Endpoint | ADMIN | ANALYST | VIEWER | Public |
|----------|-------|---------|--------|--------|
| `GET /` | ✅ | ✅ | ✅ | ✅ |
| `GET /health` | ✅ | ✅ | ✅ | ✅ |
| `POST /log` | ✅ | ✅ | ✅ | ✅ |
| `POST /login` | ✅ | ✅ | ✅ | ✅ |
| `GET /realtime-dashboard` | ✅ | ✅ | ✅ | 🔒 |
| `GET /analytics` | ✅ | ✅ | ❌ | 🔒 |
| `GET /anomalies` | ✅ | ✅ | ❌ | 🔒 |
| `GET /ml-anomalies` | ✅ | ✅ | ❌ | 🔒 |
| `GET /alerts` | ✅ | ✅ | ❌ | 🔒 |
| `GET /investigation/{id}` | ✅ | ✅ | ❌ | 🔒 |
| `GET /incident-report/{id}` | ✅ | ✅ | ❌ | 🔒 |
| `GET /user-baselines` | ✅ | ❌ | ❌ | 🔒 |
| `POST /register` | ✅ | ❌ | ❌ | 🔒* |

*When `AUTH_REQUIRED=true`. When `AUTH_REQUIRED=false`, RBAC is bypassed for development.

---

## MITRE ATT&CK Mapping Strategy

**Service:** `app/services/mitre_mapping_service.py`

### Mapping Rules

| Detection Pattern | Technique ID | Technique Name |
|-------------------|--------------|----------------|
| Repeated Failed Logins | T1110 | Brute Force |
| Successful Login After Failures | T1078 | Valid Accounts |
| Account Enumeration | T1087 | Account Discovery |
| Unusual Login Behavior / ML Outlier / Baseline Deviation | T1078 | Valid Accounts |
| Risk Spikes (score ≥ 90) | T1499 | Endpoint Denial of Service |
| Default / unknown | T1071 | Application Layer Protocol |

### Response Format

```json
{
  "technique_id": "T1110",
  "technique_name": "Brute Force"
}
```

MITRE mappings are stored on alert creation in the `alerts` table (`mitre_technique_id`, `mitre_technique_name`).

---

## Investigation Workflow

### Endpoint

`GET /investigation/{alert_id}`

### Analyst Workflow

1. **Triage** — Review alerts via `GET /alerts` or dashboard Investigation panel
2. **Investigate** — Select alert to load full investigation view
3. **Analyze** — Review timeline, evidence artifacts, MITRE mapping
4. **Respond** — Follow recommended action guidance
5. **Report** — Export JSON incident report

### Investigation Response

```json
{
  "alert_id": 1,
  "severity": "HIGH",
  "user": "alice",
  "source_ip": "Russia",
  "timeline": [...],
  "evidence": [...],
  "risk_score": 85,
  "mitre_mapping": {
    "technique_id": "T1078",
    "technique_name": "Valid Accounts"
  },
  "recommended_action": "PRIORITY: Validate user identity..."
}
```

---

## Incident Reporting Workflow

### Endpoint

`GET /incident-report/{alert_id}`

### Report Sections

1. **Executive Summary** — Non-technical overview for leadership
2. **Alert Details** — User, severity, source, timestamp
3. **Evidence** — Log and anomaly artifacts
4. **MITRE Techniques** — Mapped ATT&CK techniques with tactics
5. **Risk Assessment** — Score, level, confidence estimate
6. **Recommendations** — Prioritized response actions

### Export

The React dashboard Investigation panel includes an **Export Incident Report** button that downloads the JSON report as `incident-report-{id}.json`.

---

## Docker Deployment

### Quick Start

```bash
docker compose up --build
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| backend | 8000 | FastAPI + SQLite (persisted volume) |
| frontend | 3000 | Nginx serving React production build |

### Environment

Docker Compose sets `AUTH_REQUIRED=true` by default. Login with:

- **Username:** `admin`
- **Password:** `Admin123!`

### Volumes

- `backend_data` — SQLite database persistence
- `./models` — ML model artifacts (mounted read-only)

---

## Database Changes (Phase 12)

### New Table: `users`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| username | TEXT UNIQUE | Login username |
| email | TEXT UNIQUE | Email address |
| password_hash | TEXT | bcrypt hash |
| role | TEXT | ADMIN, ANALYST, VIEWER |
| created_at | TEXT | UTC timestamp |

### Extended Table: `alerts`

| New Column | Type | Description |
|------------|------|-------------|
| source_ip | TEXT | Source location/IP at alert time |
| mitre_technique_id | TEXT | MITRE technique ID |
| mitre_technique_name | TEXT | MITRE technique name |

All migrations are idempotent via `_add_column_if_missing()`.

---

## Frontend Enhancements

| Component | Purpose |
|-----------|---------|
| `LoginPage.js` | JWT authentication screen |
| `AuthContext.js` | Token storage, authFetch, role checks |
| `MitreAttackCard.js` | MITRE ATT&CK technique dashboard card |
| `InvestigationPanel.js` | SOC investigation workbench + report export |
| `Sidebar.js` | Role-based navigation visibility |

---

## Related Documentation

- [architecture.md](architecture.md) — Updated system architecture
- [phase12_validation_report.md](phase12_validation_report.md) — Test results
