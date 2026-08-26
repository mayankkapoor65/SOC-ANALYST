# Changelog

All notable changes to **SentinelAI — Security Log Anomaly Detection** are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.0.1] — 2026-08-13

### Fixed
- Threat intelligence feed parsing: non-numeric `threat_score` values default to 0 with warning instead of crashing
- Correlation engine: Account Takeover no longer fires for users without an established behavioral baseline

### Added
- Regression tests for threat feed edge cases and correlation baseline guard
- Patch report: `docs/v1.0.1_patch_report.md`

---

## [1.0.0] — 2026-08-13

### Added — Phase 15: Explainable AI
- SHAP TreeExplainer for Isolation Forest anomaly explanations
- `GET /ml-explanation/{log_id}` endpoint
- Explainability panel in SentinelAI dashboard
- Deviation-based fallback when model unavailable

### Added — Phase 14: SIEM Correlation Engine
- Multi-event attack chain detection (4 rules)
- Credential Stuffing, Account Takeover, Insider Threat, Impossible Travel
- `GET /correlation-alerts`, `GET /correlation-alerts/{id}`
- Correlation alerts panel with recommended SOC actions

### Added — Phase 13: Threat Intelligence
- Pluggable IOC feed (JSON, CSV, mock fallback)
- IP and location enrichment at ingestion time
- `GET /threat-intel`, `GET /threat-intel/ip/{ip}`
- Threat Intel dashboard panel

### Added — Phase 12.2: Demo User Management + Guest Access
- Idempotent seeding of 10 demo accounts (ADMIN, ANALYST, VIEWER)
- "Continue as Guest" on login page (temporary VIEWER session)
- Demo credentials card on login UI

### Added — Phase 12.1: Hardening
- Confidence score clamping to [0, 1]
- Hybrid risk score consistency across API and DB
- Admin/JWT security startup validation
- Expanded unit test coverage (JWT, RBAC, ML loading)

### Added — Phase 12: SOC Platform
- JWT authentication with bcrypt password hashing
- RBAC: ADMIN, ANALYST, VIEWER roles
- MITRE ATT&CK technique mapping on alerts
- Investigation workbench and incident report endpoints
- Docker Compose deployment (backend + frontend)
- SentinelAI SOC dashboard redesign

### Added — Phase 11: Hybrid ML Detection
- Isolation Forest unsupervised anomaly detection
- User behavioral baselines (device, location, login hour, frequency)
- Hybrid detection engine combining rules + ML + baselines
- Advanced composite risk scoring
- ML training script (`train_model.py`)
- ML anomaly dashboard cards

### Added — Phases 1–10: Core Platform
- FastAPI log ingestion (`POST /log`)
- Rule-based risk scoring (location + device signals)
- Anomaly detection and alert generation
- SQLite persistence
- Analytics and realtime dashboard APIs
- React dashboard with Recharts visualizations
- Log generator for demo and testing

---

## Phase Milestones

| Phase | Focus | Status |
|-------|-------|--------|
| 1–10 | Core ingestion, scoring, dashboard | Complete |
| 11 | Hybrid ML (Isolation Forest + baselines) | Complete |
| 12 | JWT, RBAC, MITRE, Docker, SOC UI | Complete |
| 12.1 | Security hardening | Complete |
| 12.2 | Demo users + guest access | Complete |
| 13 | Threat intelligence | Complete |
| 14 | Correlation engine | Complete |
| 15 | Explainable AI (SHAP) | Complete |

---

## [Unreleased]

### Planned
- ONNX/skops model format (replace pickle deserialization)
- Rate limiting on `POST /log`
- E2E integration tests (Playwright)
- External threat feed integrations (AbuseIPDB, OTX)
