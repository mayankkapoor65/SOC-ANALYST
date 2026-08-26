# Technical Report — SentinelAI Security Log Anomaly Detection

**Version:** 1.0.1  
**Date:** August 2026  
**Author:** Pragna  
**Classification:** Portfolio / Technical Documentation

---

## Executive Summary

SentinelAI is a full-stack Mini-SIEM platform that ingests authentication logs, applies hybrid detection (rules + machine learning + behavioral baselines), enriches events with threat intelligence, correlates multi-step attack chains, and presents analyst-ready intelligence through a React SOC dashboard.

The system demonstrates production-oriented patterns — JWT authentication, RBAC, structured logging, Docker deployment, and 38 unit tests — while remaining lightweight enough for local development and portfolio demonstration.

---

## System Overview

| Attribute | Detail |
|-----------|--------|
| Architecture | Layered monolith (FastAPI + SQLite + React) |
| Ingestion | REST API (`POST /log`) |
| Detection | Hybrid: rules, Isolation Forest, baselines |
| Storage | SQLite (7 tables) |
| Frontend | React 18, Recharts, 5-second polling |
| Auth | JWT (HS256), bcrypt, RBAC (3 roles) |
| Deployment | Docker Compose, uvicorn, nginx |

---

## Technology Stack

### Backend
- **Python 3.9+**, FastAPI, Uvicorn
- **scikit-learn** — Isolation Forest, StandardScaler
- **SHAP** — TreeExplainer for ML attribution
- **python-jose** — JWT handling
- **bcrypt** — Password hashing
- **SQLite** — Embedded persistence

### Frontend
- **React 18** (Create React App)
- **Recharts** — Data visualization
- **Custom CSS** — SentinelAI SOC theme

### DevOps
- **Docker** + **Docker Compose**
- **nginx** — Frontend static serving
- **python-dotenv** — Configuration

---

## Core Components

### 1. Ingestion Layer
- Pydantic-validated log schema
- Public endpoint for log shippers and generators
- Atomic pipeline: score → persist → detect → correlate → enrich

### 2. Detection Layer
- **Rule engine:** Location and device signals (max score 100)
- **Isolation Forest:** 4-feature unsupervised outlier detection
- **Baseline service:** Per-user behavioral profiling
- **Hybrid combiner:** Weighted composite with confidence clamping

### 3. Intelligence Layer
- **Threat feeds:** JSON/CSV/mock IOC sources (17 default indicators)
- **Correlation engine:** 4 attack chain rules
- **MITRE ATT&CK:** Technique mapping on alerts

### 4. Presentation Layer
- Real-time dashboard with live feed
- Analytics, threat intel, correlation, and explainability panels
- Investigation workbench with incident reports
- Role-based navigation (ADMIN / ANALYST / VIEWER)

---

## Data Model

| Table | Purpose |
|-------|---------|
| `security_logs` | All ingested events with hybrid scores |
| `alerts` | HIGH/CRITICAL alerts with MITRE mapping |
| `anomalies` | Detected anomaly records |
| `user_baselines` | Behavioral profiles |
| `users` | Authentication accounts |
| `correlation_alerts` | Multi-event attack chains |

---

## Security Architecture

| Control | Implementation |
|---------|----------------|
| Authentication | JWT Bearer tokens |
| Authorization | RBAC with FastAPI dependencies |
| Password storage | bcrypt hashed |
| Input validation | Pydantic schemas |
| SQL injection | Parameterized queries |
| Model loading | Path allowlisting + filename validation |
| CORS | Configurable via environment |

### Known Limitations
- Pickle model deserialization (documented; ONNX migration planned)
- `POST /log` intentionally public
- Default credentials for demo use

---

## Performance Characteristics

| Endpoint | Typical Response |
|----------|------------------|
| `/health` | < 5 ms |
| `/realtime-dashboard` | < 5 ms |
| `/analytics` | ~65–100 ms (aggregates sub-services + SHAP) |
| `/ml-explanation/{id}` | ~4 ms warm / ~1 s cold |
| SHAP peak memory | ~17 MB per request |

---

## Testing

| Suite | Count | Coverage |
|-------|-------|----------|
| Backend unit tests | 38 | Auth, RBAC, ML loading, confidence, threat intel, correlation |
| Frontend tests | 1 | Dashboard render |
| Phase validation reports | 6 | Integration verification per phase |

---

## Deployment Options

### Local Development
```bash
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
cd frontend && npm start
```

### Docker
```bash
docker compose up --build
```

Backend: `http://localhost:8000`  
Frontend: `http://localhost:3000`

---

## Audit Results Summary

From [final_release_audit.md](final_release_audit.md):

| Metric | Score |
|--------|-------|
| Production Readiness | 91/100 |
| Portfolio Readiness | 96/100 |

All core endpoints regression-tested. Docker runtime verification pending on audit host.

---

## Related Documentation

- [architecture.md](architecture.md)
- [detection_logic.md](detection_logic.md)
- [ml_detection.md](ml_detection.md)
- [release_v1.0.0.md](release_v1.0.0.md)
- [final_release_audit.md](final_release_audit.md)
