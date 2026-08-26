# Presentation Q&A — Top 30 Likely Interviewer Questions

Suggested answers for Security Log Anomaly Detection / SentinelAI presentations.

---

## Architecture & Design

### 1. What problem does this project solve?

**Answer:** Security teams drown in login logs and miss early compromise signals. SentinelAI automates ingestion, risk scoring, anomaly detection, and attack chain correlation — giving analysts a focused SOC dashboard instead of manual log review.

---

### 2. Why FastAPI and SQLite instead of Elasticsearch or Splunk?

**Answer:** FastAPI gives async performance with automatic OpenAPI docs. SQLite keeps the project portable, zero-config, and demo-friendly — ideal for a portfolio Mini-SIEM. The architecture is designed so the database layer can be swapped for PostgreSQL or Elasticsearch in production without changing the API contract.

---

### 3. Walk me through the data flow when a log arrives.

**Answer:** `POST /log` → rule risk scoring (location + device) → insert to SQLite → hybrid detection (Isolation Forest + baseline check) → advanced risk composite → alert if risk ≥ 80 → correlation engine (4 rules) → threat intel enrichment → SHAP explanation if ML flagged → JSON response to caller. Dashboard polls analytics every 5 seconds.

---

### 4. Why a hybrid detection approach instead of rules-only or ML-only?

**Answer:** Rules catch known bad patterns (Russia login, unknown device) with explainability. ML catches statistical outliers rules miss. Baselines detect behavioral drift per user. Combining all three with confidence scoring reduces both false negatives and blind spots.

---

### 5. How is the frontend connected to the backend?

**Answer:** React dashboard polls REST endpoints every 5 seconds via `authFetch` (JWT Bearer token). AuthContext manages login state in localStorage. Role-based sidebar navigation filters views by ADMIN/ANALYST/VIEWER permissions.

---

## Machine Learning

### 6. What ML model do you use and why?

**Answer:** Isolation Forest — an unsupervised anomaly detection algorithm. It works well without labeled attack data, handles multi-dimensional feature vectors, and is fast at inference. Trained on login_hour, elevated_risk_count, event_frequency, and risk_score.

---

### 7. How do you explain ML decisions to analysts?

**Answer:** SHAP TreeExplainer provides per-feature attribution for each ML anomaly. The dashboard shows top contributing factors and a natural-language summary. If the model isn't loaded, a deviation-based fallback explanation is used.

---

### 8. How often is the model retrained?

**Answer:** Currently manual via `train_ml_model.py`. In production, I'd schedule retraining weekly on rolling windows, with model versioning and A/B comparison before deployment.

---

### 9. What's in the feature vector?

**Answer:** Four features: `login_hour` (0–23), `elevated_risk_count` (recent high-risk events for the user), `event_frequency` (recent event count), and `risk_score` (rule-based score). StandardScaler normalizes before Isolation Forest inference.

---

### 10. How do you handle model loading securely?

**Answer:** Models load from an allowlisted `models/` directory with filename validation and path traversal checks. Known gap: pickle deserialization risk — production should migrate to ONNX or skops format (documented in audit reports).

---

## Detection & Correlation

### 11. What correlation rules do you implement?

**Answer:** Four attack chains: Credential Stuffing (fail-fail-success), Account Takeover (new device → high risk → privileged access), Insider Threat (5+ high-risk events in 24h), and Impossible Travel (2+ locations within 2 hours). All scoped per user_id.

---

### 12. How do you prevent false positives in correlation?

**Answer:** Account Takeover requires an established user baseline before evaluating device deviation (v1.0.1 fix). Duplicate alerts are suppressed within a 1-hour window. Rules use minimum event counts and time windows to avoid single-event triggers.

---

### 13. How does risk scoring work?

**Answer:** Base score 20. +40 for high-risk locations (Russia, China). +40 for unknown devices. Hybrid risk combines rule score with ML score and baseline deviation via weighted formula. Alerts fire at hybrid risk ≥ 80.

---

### 14. What is behavioral baseline tracking?

**Answer:** Per-user profiles store typical device, login hour, location, and event frequency. Before each log updates the baseline, the system checks for deviation — unusual hour (±4h), new device, new location, or frequency spike.

---

### 15. How does MITRE ATT&CK mapping work?

**Answer:** Alerts are mapped to technique IDs based on event type, anomaly type, and description keywords. E.g., failed logins → T1110 (Brute Force), successful logins → T1078 (Valid Accounts). Each alert includes technique name and recommended SOC action.

---

## Security

### 16. How does authentication work?

**Answer:** JWT tokens (HS256) with bcrypt password hashing. Three RBAC roles: ADMIN (full access), ANALYST (analytics + investigation), VIEWER (dashboard only). FastAPI dependency injection enforces permissions per endpoint. Returns 401 for auth failures, 403 for insufficient role.

---

### 17. Is POST /log protected?

**Answer:** Intentionally public — it's the ingestion endpoint designed for log shippers and generators. In production, I'd add API key authentication or network-level restrictions (IP allowlist, mTLS).

---

### 18. What are the main security risks in the current implementation?

**Answer:** Three: (1) pickle model deserialization — migrate to ONNX; (2) AUTH_REQUIRED=false in local dev bypasses auth; (3) no rate limiting on POST /log. All documented in the final release audit with remediation paths.

---

### 19. How are passwords stored?

**Answer:** bcrypt hashed with per-user salt. Default admin is seeded on first startup. Insecure default passwords are blocked when AUTH_REQUIRED=true.

---

### 20. How do you prevent SQL injection?

**Answer:** All database queries use parameterized statements (? placeholders). f-strings are only used for hardcoded table/column names in schema migrations, never for user input.

---

## Threat Intelligence

### 21. Where does threat intelligence data come from?

**Answer:** Pluggable feed system supporting JSON, CSV, or built-in mock. Default feed is `sample_data/threat_feed.json` with 17 IOCs. Designed for future integration with AbuseIPDB, AlienVault OTX, or VirusTotal.

---

### 22. How is threat intel matched to events?

**Answer:** At ingestion time, `enrich_ioc()` checks source IP and location against the in-memory IOC cache. Matches return threat score, category, confidence, and a human-readable context string in the API response.

---

## DevOps & Testing

### 23. How do you deploy this?

**Answer:** Docker Compose with two services: backend (Python 3.11 + uvicorn on 8000) and frontend (nginx serving React build on 3000). Backend sets AUTH_REQUIRED=true, mounts models volume, and persists SQLite to a named volume.

---

### 24. What testing do you have?

**Answer:** 35 backend unit tests covering confidence clamping, JWT auth, RBAC, ML loading security, threat intel, and correlation. 1 frontend test for dashboard rendering. Phase validation reports document API integration testing.

---

### 25. How would you scale this for production?

**Answer:** Replace SQLite with PostgreSQL, add Redis for feed caching, deploy behind nginx with TLS, migrate models to ONNX, add rate limiting, enable AUTH_REQUIRED, rotate JWT secrets, and queue log ingestion via Kafka/RabbitMQ for burst handling.

---

## Project-Specific

### 26. What was the hardest part to build?

**Answer:** The hybrid detection pipeline — getting rule scores, ML scores, and baseline deviations to combine into a meaningful composite risk with proper confidence clamping, while keeping POST /log backward compatible and response times under 100ms.

---

### 27. What would you improve next?

**Answer:** Three priorities: (1) ONNX model format to eliminate pickle risk, (2) rate limiting and API key auth on ingestion, (3) E2E integration tests with Playwright for the full login-to-dashboard flow.

---

### 28. How is this different from a SIEM like Splunk or QRadar?

**Answer:** It's a lightweight Mini-SIEM focused on authentication log analysis — not a full enterprise SIEM. But it implements core SOC capabilities: ingestion, detection, correlation, threat intel, explainability, investigation workflow, and RBAC — at a scale suitable for demos, labs, and SMB deployments.

---

### 29. Can you show me the correlation engine code?

**Answer:** "Yes — `app/services/correlation_engine.py`. Each rule fetches recent logs filtered by user_id and time window, checks a specific pattern, and inserts a correlation alert with deduplication. Happy to walk through the credential stuffing rule line by line."

---

### 30. Why should we hire you based on this project?

**Answer:** This project demonstrates full-stack security engineering — not just coding. I designed the detection pipeline, implemented ML with explainability, built correlation rules modeled on real SOC playbooks, added JWT/RBAC, wrote 35 tests, containerized with Docker, and documented every phase with audit reports. It shows I can take a security problem from architecture to working demo.

---

## Bonus Rapid-Fire Answers

| Question | One-Line Answer |
|----------|----------------|
| React version? | CRA with React 18, Recharts for visualization |
| Database schema? | 7 tables: security_logs, alerts, anomalies, user_baselines, users, correlation_alerts |
| API version? | v1.0.0 (v1.0.1 patch for TI + correlation fixes) |
| Default login? | admin / Admin123! |
| How many IOCs? | 17 in default threat feed |
| Polling interval? | 5 seconds |
| ML training script? | `train_ml_model.py` |
| Log generator? | `log_generator.py` — random events every 2 seconds |

---

*Review this document 15 minutes before your presentation. Pick the 5–8 questions most relevant to your interviewer’s role (security vs ML vs full-stack).*
