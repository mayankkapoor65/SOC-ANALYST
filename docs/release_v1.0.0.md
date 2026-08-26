# Release Notes — v1.0.0

**Product:** SentinelAI — Security Log Anomaly Detection  
**Release Date:** August 13, 2026  
**Version:** 1.0.0 (patch: 1.0.1)

---

## Executive Summary

Version 1.0.0 marks the first complete release of SentinelAI, a portfolio-grade Mini-SIEM platform. The release delivers end-to-end security log analysis — from ingestion through hybrid detection, threat intelligence, attack chain correlation, and explainable AI — packaged in a modern SOC dashboard with enterprise authentication patterns.

This release is optimized for **demonstrations, internships, cybersecurity portfolios, and Master's program applications**.

---

## Key Features

| Category | Capability |
|----------|------------|
| Ingestion | REST API log pipeline with real-time processing |
| Detection | Hybrid rule + ML + baseline engine |
| Visualization | SentinelAI React SOC dashboard |
| Intelligence | Threat feed enrichment (17 IOCs) |
| Correlation | 4 attack chain detection rules |
| Explainability | SHAP feature attribution |
| Auth | JWT + RBAC (ADMIN / ANALYST / VIEWER) |
| Deployment | Docker Compose ready |

---

## Security Features

- JWT authentication with configurable expiry
- bcrypt password hashing
- Role-based access control on all read endpoints
- MITRE ATT&CK technique mapping on alerts
- Investigation workbench with recommended actions
- Incident report generation (JSON export)
- Security startup validation when `AUTH_REQUIRED=true`
- Demo account seeding + guest access (v1.0.1 / Phase 12.2)

---

## ML Features

- **Isolation Forest** unsupervised anomaly detection
- **4-feature vector:** login hour, elevated risk count, event frequency, risk score
- **StandardScaler** normalization
- **User behavioral baselines** with deviation detection
- **Hybrid confidence scoring** clamped to [0, 1]
- **SHAP TreeExplainer** for analyst-trustworthy explanations
- Training script: `train_model.py`

---

## Threat Intelligence

- Pluggable feed backends: JSON, CSV, built-in mock
- 17 default IOCs (botnets, scanners, malicious geographies)
- IP and location matching at ingestion time
- Dashboard panel with category breakdown and metrics
- API: `GET /threat-intel`, `GET /threat-intel/ip/{ip}`

---

## Correlation Engine

| Rule | Severity | Pattern |
|------|----------|---------|
| Credential Stuffing | HIGH | fail → fail → success |
| Account Takeover | CRITICAL | new device → high risk → privileged |
| Insider Threat | HIGH | ≥5 high-risk events / 24h |
| Impossible Travel | HIGH | multiple locations / 2h |

Scoped per user. Duplicate suppression within 1 hour.

---

## Explainable AI

- SHAP attributions for ML anomalies
- Top contributing features with natural-language summaries
- Fallback explanation when model unavailable
- Integrated in analytics and dedicated dashboard panel
- On-demand endpoint: `GET /ml-explanation/{log_id}`

---

## Demo Accounts (Phase 12.2)

| Role | Username | Password |
|------|----------|----------|
| ADMIN | admin | Admin123! |
| ANALYST | analyst1 | Analyst123! |
| VIEWER | viewer1 | Viewer123! |

Additional accounts: `admin1–3`, `analyst1–3`, `viewer1–3`.  
Guest access available via **Continue as Guest** on login page.

---

## Known Limitations

1. **Pickle model format** — RCE risk if model files tampered; migrate to ONNX/skops recommended
2. **SQLite** — Not suitable for high-volume production without migration to PostgreSQL
3. **POST /log public** — No built-in rate limiting
4. **Default credentials** — Must be rotated before public deployment
5. **Docker runtime** — Compose config validated; live deployment environment-dependent
6. **SHAP cold start** — First analytics call may take ~1 second

---

## Future Roadmap

| Priority | Enhancement |
|----------|-------------|
| High | ONNX/skops model serialization |
| High | Rate limiting + API key auth on ingestion |
| Medium | E2E tests (Playwright) |
| Medium | External threat feeds (AbuseIPDB, OTX) |
| Medium | PostgreSQL support |
| Low | Email/Slack alert notifications |
| Low | Geo-velocity impossible travel (coordinate-based) |

---

## Documentation Index

- [README.md](../README.md) — Quick start
- [CHANGELOG.md](../CHANGELOG.md) — Version history
- [architecture.md](architecture.md) — System design
- [detection_logic.md](detection_logic.md) — Detection pipeline
- [final_release_audit.md](final_release_audit.md) — Release audit
- [demo_script.md](demo_script.md) — Presentation guide

---

*v1.0.0 — SentinelAI Security Log Anomaly Detection*
