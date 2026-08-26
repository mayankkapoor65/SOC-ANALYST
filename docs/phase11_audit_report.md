# Phase 11 Independent Audit Report

**Audit Date:** 2026-08-13  
**Auditor Role:** Principal Security Architect / Senior ML Engineer / Senior Backend Engineer  
**Scope:** Phase 11 Hybrid Rule + ML Detection (post–Phase 11.1 remediation)  
**Method:** Static code review, runtime simulation, edge-case testing, live API verification  
**Rule:** Review actual implementation only — no code changes made during this audit.

---

## Executive Summary

Phase 11 delivers a functional hybrid detection pipeline combining rule-based scoring, Isolation Forest ML, and behavioral baselines. Phase 11.1 remediation successfully addressed the five production-critical defects identified in the prior audit (baseline ordering, corrupt-model crashes, UTC timestamps, feature scaling, API `risk_score` semantics).

The system is **suitable for demos, portfolios, and controlled pilot environments**. It is **not yet production-ready** for enterprise SOC deployment due to remaining security gaps (no authentication, pickle deserialization), several medium-severity logic issues, and internal data-semantics inconsistencies.

**Overall Production Readiness: 83/100 — Good (approaching Strong)**

### Top Remaining Risks

| Priority | Issue | Impact |
|----------|-------|--------|
| P1 | No API authentication | Any client can ingest logs and read all data |
| P1 | Pickle model deserialization | RCE if `models/` directory is writable by an attacker |
| P2 | Confidence score can go negative or crash on `None` | Invalid stored values break POST /log |
| P2 | DB `risk_score` column stores hybrid score; API returns rule score | Analytics/dashboard drift from API semantics |
| P3 | Baseline frequency compares 1-hour count vs 24-hour baseline | False negatives on burst detection |
| P3 | 17 orphaned service modules | Maintenance burden, confusion |

---

## PASS / FAIL Summary

| Audit | Area | Result | Notes |
|-------|------|--------|-------|
| 1 | Isolation Forest Validation | **PASS** (with findings) | Core ML correct post-11.1; feature-engineering gaps remain |
| 2 | Confidence Score Validation | **FAIL** | Can go negative; crashes on `None`; misleading rule branch |
| 3 | Advanced Risk Score Review | **PASS** (with findings) | Formula sound; DB/API semantic split is a concern |
| 4 | Database Migration Safety | **PASS** | All three migration scenarios verified |
| 5 | API Compatibility | **PASS** (with findings) | Response fields backward compatible; DB column semantics differ |
| 6 | Dashboard Compatibility | **PASS** | Null-safe; empty states handled; 1 unit test passes |
| 7 | Baseline Detection | **PASS** (with findings) | Core logic works post reorder fix; frequency window bug |
| 8 | Model Resilience | **PASS** | Graceful degradation verified for all simulated failures |
| 9 | Security Review | **FAIL** | No auth, pickle risk, open CORS |
| 10 | Production Readiness | **83/100** | Good tier |

---

## Audit 1 — Isolation Forest Validation

**Result: PASS (with findings)**

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Correctly implemented | ✅ PASS | sklearn `IsolationForest` with `random_state=42`, `n_estimators=100` |
| 2 | Feature normalization | ✅ PASS | `StandardScaler` fit at train time, applied at inference (lines 209–210, 279) |
| 3 | Small datasets handled | ✅ PASS | `MIN_TRAINING_SAMPLES=10`; returns `None` below threshold |
| 4 | Training cannot crash on low data | ✅ PASS | Guard at line 202–207; `train_model.py` exits cleanly |
| 5 | Predictions deterministic | ✅ PASS | Identical outputs on repeated calls with `random_state=42` |
| 6 | Model loading errors handled | ✅ PASS | `_safe_joblib_load()` catches all exceptions, returns `None` |
| 7 | Missing model file handled | ✅ PASS | Returns `model_ready=false`; auto-train if ≥10 DB rows |
| 8 | Invalid data cannot break inference | ⚠️ PARTIAL | Null inputs do not crash but produce inference; no NaN guard |

### Findings

| Severity | File | Line(s) | Issue | Fix Recommendation |
|----------|------|---------|-------|-------------------|
| MEDIUM | `app/services/ml_anomaly_service.py` | 116, 164 | `login_hour` (0–23) treated as linear feature; hour 23 and hour 0 appear far apart | Encode hour cyclically (sin/cos) or use domain-specific bins |
| MEDIUM | `app/services/ml_anomaly_service.py` | 264–295 | `None` for `risk_score`/`login_hour` does not raise but produces ML scores | Validate inputs; coerce or reject before inference |
| LOW | `app/services/ml_anomaly_service.py` | 253–261 | Auto-train on first request can add latency on cold start with large DB | Pre-train via `train_model.py` at deploy; disable auto-train in production |
| LOW | `app/services/ml_anomaly_service.py` | 288–289 | Non-anomaly scores artificially damped to 30% of raw score | Document behavior; consider exposing raw score separately |
| INFO | `app/services/ml_anomaly_service.py` | 212 | Contamination formula `min(0.2, max(0.05, 5/n))` is reasonable | No change required |

---

## Audit 2 — Confidence Score Validation

**Result: FAIL**

Reviewed: `calculate_confidence()` in `app/services/hybrid_detection_service.py` (lines 11–22)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Logically derived | ⚠️ PARTIAL | Weighted sum: rule 45%, ML 35%, baseline 20% |
| 2 | Range 0–1 | ❌ FAIL | Negative inputs produce negative output |
| 3 | Cannot become negative | ❌ FAIL | `ml_score=-0.5` → `confidence=-0.17` |
| 4 | Cannot exceed 1 | ✅ PASS | `min(confidence, 1.0)` caps upper bound |
| 5 | Meaningful interpretation | ⚠️ PARTIAL | Weights are reasonable but rule branch is misleading |

### Findings

| Severity | File | Line(s) | Issue | Fix Recommendation |
|----------|------|---------|-------|-------------------|
| HIGH | `app/services/hybrid_detection_service.py` | 11–22 | No lower-bound clamp; negative `ml_score` or `deviation_score` yields negative confidence | Apply `max(0.0, min(confidence, 1.0))` and clamp inputs |
| HIGH | `app/services/hybrid_detection_service.py` | 18 | `None` ml_score causes `TypeError`, crashing POST /log | Use `(ml_score or 0)` before arithmetic |
| MEDIUM | `app/services/hybrid_detection_service.py` | 16 | `rule_score <= 1` branch treats score as 0–1 probability, but rule scores are 0–100 integers | Remove `<= 1` branch; normalize rule score as `rule_score / 100` |
| LOW | `app/services/hybrid_detection_service.py` | 11–22 | Confidence is a heuristic weighted sum, not calibrated probability | Document as "signal strength" not "probability"; consider Platt scaling in Phase 12 |

### Runtime Evidence

```
ml_score=-0.5  → confidence=-0.17  (OUT OF RANGE)
ml_score=None  → TypeError crash
ml_score=1.5   → confidence=0.52   (uncapped input, capped output)
all signals max → confidence=0.98
```

---

## Audit 3 — Advanced Risk Score Review

**Result: PASS (with findings)**

Reviewed: `app/services/advanced_risk_service.py`

**Formula:** `final = min(rule_score + (ml_score × 20) + deviation_score, 100)`  
**Hybrid floor:** When `hybrid_anomaly=True`, minimum final risk = 50 (MEDIUM)

| # | Check | Result |
|---|-------|--------|
| 1 | Mathematically sound | ✅ PASS |
| 2 | Score capped at 100 | ✅ PASS |
| 3 | Risk inflation bounded | ✅ PASS — max additions: ML=19, deviation=30 |
| 4 | Thresholds reasonable | ✅ PASS — 50/80/90 align with frontend |
| 5 | ML influence justified | ✅ PASS — 20× multiplier gives ML meaningful but not dominant weight |

### Scenario Test Results

| Scenario | rule | ml | dev | hybrid | Final Score | Level |
|----------|------|----|-----|--------|-------------|-------|
| Normal activity | 20 | 0.0 | 0 | false | **20** | LOW |
| Medium anomaly | 60 | 0.3 | 10 | true | **76** | MEDIUM |
| High anomaly | 80 | 0.7 | 20 | true | **100** | CRITICAL (capped) |
| Extreme anomaly | 100 | 0.95 | 30 | true | **100** | CRITICAL (capped) |
| ML-only lift | 20 | 0.92 | 10 | true | **50** | MEDIUM (floor applied) |
| Rule-only, no hybrid flag | 60 | 0.0 | 0 | false | **60** | MEDIUM |

### Findings

| Severity | File | Line(s) | Issue | Fix Recommendation |
|----------|------|---------|-------|-------------------|
| MEDIUM | `main.py` | 182–199 | DB `risk_score` column overwritten with `hybrid_risk_score`; API returns rule score in `risk_score` | Store hybrid score in dedicated column only; keep `risk_score` as rule score in DB |
| LOW | `app/services/advanced_risk_service.py` | 20–21 | Hybrid floor forces MEDIUM for ML-only detections on LOW rule events | Document as intentional; consider configurable floor |
| LOW | `app/services/realtime_dashboard_service.py` | 31–38 | Dashboard risk buckets use DB `risk_score` (hybrid), not rule score | Align dashboard with explicit `hybrid_risk_score` field |

---

## Audit 4 — Database Migration Safety

**Result: PASS**

Reviewed: `app/database/database.py`

| Scenario | Result | Details |
|----------|--------|---------|
| A — Fresh database | ✅ PASS | 14 `security_logs` columns, 10 `anomalies` columns, 0 rows |
| B — Phase 10 database | ✅ PASS | Legacy data preserved; Phase 11 columns added; 1 row intact |
| C — Partially upgraded | ✅ PASS | Existing `login_hour`/`ml_anomaly` not duplicated; missing cols added |
| Double `initialize_database()` | ✅ PASS | No duplicate columns (14 unique) |

| # | Check | Result |
|---|-------|--------|
| No duplicate columns | ✅ PASS | `_add_column_if_missing()` checks `PRAGMA table_info` |
| No startup crashes | ✅ PASS | All scenarios complete without exception |
| No data loss | ✅ PASS | Phase 10 row count preserved |

### Findings

| Severity | File | Line(s) | Issue | Fix Recommendation |
|----------|------|---------|-------|-------------------|
| LOW | `app/database/database.py` | 18, 25 | f-string SQL for DDL with hardcoded table/column names | Acceptable now; use allowlist validation if dynamic |
| INFO | `app/database/database.py` | 103 | `typical_ip` column stores location string, not IP | Rename to `typical_location` in Phase 12 migration |

---

## Audit 5 — API Compatibility

**Result: PASS (with findings)**

All endpoints verified live against running server.

| Endpoint | Status | Keys Present |
|----------|--------|--------------|
| GET `/` | 200 | `message`, `version` |
| GET `/health` | 200 | `status`, `database` |
| GET `/analytics` | 200 | 7 top-level keys including `hybrid_stats`, `ml_stats` |
| GET `/realtime-dashboard` | 200 | 5 keys unchanged |
| GET `/anomalies` | 200 | 7 keys; Phase 11 fields additive |
| POST `/log` | 200 | All legacy + new fields present |

### POST /log Backward Compatibility

| Legacy Field | Present | Value Semantics |
|--------------|---------|-----------------|
| `status` | ✅ | `"success"` |
| `risk_score` | ✅ | Rule score (restored in 11.1) |
| `risk_level` | ✅ | Based on hybrid score |
| `anomaly_detected` | ✅ | Hybrid flag |
| `anomaly_score` | ✅ | Combined anomaly score |
| `anomaly_type` | ✅ | Preserved |

| New Additive Field | Present |
|--------------------|---------|
| `rule_risk_score` | ✅ |
| `hybrid_risk_score` | ✅ |
| `rule_anomaly` | ✅ |
| `ml_anomaly` | ✅ |
| `baseline_deviation` | ✅ |
| `confidence` | ✅ |

**Verified:** `risk_score == rule_risk_score` in API response ✅

### Findings

| Severity | File | Line(s) | Issue | Fix Recommendation |
|----------|------|---------|-------|-------------------|
| MEDIUM | `main.py` | 192 | DB persists hybrid score in `risk_score` column while API returns rule score | Internal inconsistency for DB consumers and analytics |
| LOW | `main.py` | 94–109 | New endpoints `/ml-anomalies`, `/user-baselines` not in original spec | Additive only; no breaking change |
| INFO | — | — | Request schema unchanged (`user_id`, `event_type`, `location`, `device`) | No client migration needed |

---

## Audit 6 — Dashboard Compatibility

**Result: PASS**

Reviewed: `frontend/src/App.js`, hooks, charts, and utility helpers.

| # | Check | Result |
|---|-------|--------|
| 1 | Existing charts render | ✅ PASS — RiskDonut, ThreatTimeline, RiskTrend, etc. |
| 2 | Existing cards render | ✅ PASS — MetricCard with AnimatedCounter |
| 3 | New cards handle missing data | ✅ PASS — `??` and `\|\|` fallbacks on hybrid_stats |
| 4 | New charts handle empty responses | ✅ PASS — Empty-state messages in ML/Baseline charts |
| 5 | No runtime errors possible | ✅ PASS — Optional chaining throughout |

**Frontend test:** `npm test -- --watchAll=false` → 1/1 PASS

### Findings

| Severity | File | Line(s) | Issue | Fix Recommendation |
|----------|------|---------|-------|-------------------|
| LOW | `frontend/src/components/AnomalyCenter.js` | 12 | `types` array may include `null` if `anomaly_type` is null | Filter falsy types: `.filter(Boolean)` |
| LOW | `frontend/src/components/AnomalyCenter.js` | 88 | `anomaly_score?.toFixed(2)` renders blank for undefined | Show `"—"` fallback |
| INFO | `frontend/src/App.test.js` | — | Single smoke test with mocked data | Add integration tests for empty/partial API responses |

---

## Audit 7 — Baseline Detection

**Result: PASS (with findings)**

Reviewed: `app/services/baseline_service.py`

| Scenario | Result | Details |
|----------|--------|---------|
| Brand new user | ✅ PASS | `baseline_deviation=False`, score=0 |
| Returning normal user | ✅ PASS | No deviation when location/device/hour match |
| Abnormal location | ✅ PASS | Deviation=True, score=10, reason="New location detected" |
| Abnormal device | ✅ PASS | Deviation=True, score=10 |
| Abnormal hour (≥4h diff) | ✅ PASS | Deviation=True, score=10 |
| Update-after-check ordering | ✅ PASS | `main.py` lines 158–173: deviation before update |

### Findings

| Severity | File | Line(s) | Issue | Fix Recommendation |
|----------|------|---------|-------|-------------------|
| MEDIUM | `app/services/baseline_service.py` | 65–76 vs 143–158 | `typical_event_frequency` is 24-hour count; deviation check compares against 1-hour count | Use consistent windows (both 1-hour or both 24-hour) |
| MEDIUM | `app/services/baseline_service.py` | 58, 102–137 | Column `typical_ip` stores location string, not IP address | Rename column; update API docs |
| LOW | `app/services/baseline_service.py` | 50–53 | Baseline hour is mean of last 50 log hours; slow to adapt to schedule changes | Consider exponential moving average |
| LOW | `app/services/anomaly_service.py` | 19–26 | `evaluate_rule_anomaly` includes current log in historical AVG (inserted before hybrid runs) | Exclude current `log_id` from AVG query |

---

## Audit 8 — Model Resilience

**Result: PASS**

All scenarios simulated at runtime.

| Scenario | System Behavior | Result |
|----------|-------------------|--------|
| Missing model file (empty DB) | `model_ready=false`, rule-only detection | ✅ PASS |
| Corrupted model file | POST /log returns HTTP 200; degrades gracefully | ✅ PASS |
| Empty database | No crash; ML unavailable | ✅ PASS |
| Empty logs table | Training returns None; inference degrades | ✅ PASS |
| Invalid feature values (null) | No crash; returns ML result | ⚠️ PASS (no crash, questionable scores) |
| Scaler missing, model present | `model_ready=false` | ✅ PASS |

### Findings

| Severity | File | Line(s) | Issue | Fix Recommendation |
|----------|------|---------|-------|-------------------|
| LOW | `app/services/ml_anomaly_service.py` | 253–261 | Corrupt model triggers auto-retrain attempt (may succeed if DB has data) | Log warning; do not silently retrain in production |
| INFO | — | — | POST /log survives all failure modes tested | Meets resilience requirement |

---

## Audit 9 — Security Review

**Result: FAIL**

| Area | Finding | Severity |
|------|---------|----------|
| API authentication | None — all endpoints publicly accessible | **CRITICAL** |
| CORS | Defaults to `*` (`app/core/settings.py:14`) | **HIGH** |
| Model loading | Pickle via `joblib.load` — arbitrary code execution if file tampered | **HIGH** |
| SQL injection | Parameterized queries throughout active code | ✅ PASS |
| Path traversal (models) | `_safe_realpath()` + allowlist | ✅ Mitigated |
| Input validation | Pydantic `min_length=1` on POST /log fields | ✅ PASS |
| Error handling | Generic 500 messages; no stack trace leakage | ✅ PASS |
| Rate limiting | None | **MEDIUM** |

### Findings

| Severity | File | Line(s) | Issue | Fix Recommendation |
|----------|------|---------|-------|-------------------|
| CRITICAL | `main.py` | 47–239 | No authentication or authorization on any endpoint | Add JWT/API-key middleware (Phase 12) |
| HIGH | `app/core/settings.py` | 14 | CORS allows all origins by default | Restrict to frontend origin in production |
| HIGH | `app/services/ml_anomaly_service.py` | 57 | Pickle deserialization of model artifacts | Migrate to ONNX or skops; verify checksums at load |
| MEDIUM | `main.py` | — | No rate limiting on POST /log | Add slowapi or reverse-proxy rate limits |
| LOW | `app/database/database.py` | 18 | f-string in PRAGMA (hardcoded table names) | Low risk; no user input |

---

## Audit 10 — Production Readiness Score

| Category | Score | Rationale |
|----------|-------|-----------|
| Architecture | **9/10** | Clean hybrid pipeline; proper separation of rule/ML/baseline layers; graceful degradation |
| Backend | **8/10** | Solid error handling post-11.1; DB/API semantic mismatch; confidence bug |
| ML | **8/10** | Correct IF+Scaler; deterministic; minor feature engineering gaps |
| Database | **9/10** | Idempotent migrations; safe for all three upgrade scenarios |
| Frontend | **8/10** | Null-safe SOC dashboard; good empty states; minimal test coverage |
| Security | **5/10** | No auth, open CORS, pickle RCE risk — blockers for production |
| Maintainability | **7/10** | 17 orphaned service modules; some misleading field names |

### Overall Score

**58 / 70 → 83 / 100**

**Classification: Good (70–85 band, upper end)**

| Band | Range | Status |
|------|-------|--------|
| Needs Work | <70 | — |
| **Good** | **70–85** | **← Current (83)** |
| Strong | 85–95 | Requires security hardening + confidence fix |
| Production Ready | 95+ | Requires auth, ONNX, Docker, CI/CD, comprehensive tests |

---

## Critical Issues (Must Fix Before Production)

1. **No API authentication** — Any network client can read/write security data  
   → Add JWT or API-key middleware

2. **Pickle model deserialization** — Tampered model file = remote code execution  
   → Migrate to ONNX/skops with file integrity checks

3. **Confidence score can be negative or crash** — `hybrid_detection_service.py:11–22`  
   → Clamp inputs and output to `[0.0, 1.0]`; guard against `None`

---

## Recommended Fixes (Priority Order)

| Priority | Fix | Effort | Impact |
|----------|-----|--------|--------|
| P0 | Clamp confidence to [0, 1]; handle None ml_score | 30 min | Prevents POST /log crash |
| P0 | Add API authentication (JWT) | 2–4 hrs | Security blocker |
| P1 | Align DB `risk_score` column with API semantics | 1 hr | Analytics accuracy |
| P1 | Fix baseline frequency window mismatch (1h vs 24h) | 1 hr | Detection accuracy |
| P1 | Restrict CORS to frontend origin | 15 min | Security |
| P2 | Encode login_hour cyclically for ML | 1 hr | ML accuracy |
| P2 | Migrate model format from pickle to ONNX | 4–8 hrs | Security |
| P2 | Rename `typical_ip` → `typical_location` | 1 hr | Clarity |
| P3 | Remove or archive 17 orphaned service modules | 2 hrs | Maintainability |
| P3 | Exclude current log from rule anomaly AVG query | 30 min | Detection accuracy |

---

## What Phase 11.1 Fixed (Verified)

| Prior Finding | Status |
|---------------|--------|
| Baseline update before deviation check | ✅ Fixed — check runs before update |
| Corrupt model crashes POST /log | ✅ Fixed — `_safe_joblib_load()` + try/except |
| UTC/local timestamp mismatch | ✅ Fixed — `app/core/time_utils.py` |
| No feature normalization | ✅ Fixed — StandardScaler added |
| `risk_score` API semantic change | ✅ Fixed — returns rule score; `hybrid_risk_score` added |
| ML anomaly with LOW final risk | ✅ Fixed — hybrid floor at 50 |
| O(n²) training queries | ✅ Fixed — `_build_feature_matrix()` batch builder |

---

## Test Evidence Summary

```
Advanced Risk: 6/6 scenarios produce expected scores
Confidence:    FAIL on negative inputs and None ml_score
DB Migration:  3/3 scenarios PASS, double-init PASS
ML Resilience: 6/6 scenarios PASS (no HTTP 500)
API Endpoints: 6/6 return 200 with expected schemas
Baseline:      6/6 behavioral scenarios behave correctly
Frontend:      1/1 unit test PASS
POST /log:     risk_score == rule_risk_score verified
Corrupt model: HTTP 200 (no crash)
```

---

*Report generated by independent audit. No code was modified during this review.*
