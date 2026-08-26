# 10-Minute Technical Demo Walkthrough

**Audience:** Technical interviewers, security engineers, ML engineers  
**Goal:** Demonstrate architecture depth, detection pipeline, and engineering decisions

---

## Setup (Before Demo)

```bash
# Terminal 1 — Backend
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — Frontend
cd frontend && npm start

# Terminal 3 — Load demo data (once)
python3 -c "
import json, requests
for e in json.load(open('sample_data/demo_logs.json')):
    p = {k:v for k,v in e.items() if k in ('user_id','event_type','location','device','source_ip') and v}
    requests.post('http://127.0.0.1:8000/log', json=p)
print('Demo data loaded')
"
```

---

## Segment 1: Architecture Overview (1:30)

**Say:**
> "The pipeline is: Log Generator → FastAPI ingestion → Rule scoring → Hybrid detection (Isolation Forest + baselines) → Advanced risk composite → Correlation engine → Threat intel enrichment → SQLite → Analytics API → React dashboard."

**Show:** Open `http://127.0.0.1:8000/docs` briefly — highlight `POST /log`, `GET /analytics`, `GET /correlation-alerts`.

**Do:** `curl http://127.0.0.1:8000/` — show version and `auth_required` flag.

**Expected:**
```json
{"message": "Security Log Anomaly Detection System Running", "version": "1.0.0", "auth_required": false}
```

---

## Segment 2: Log Ingestion & Risk Scoring (1:30)

**Do:** POST a high-risk event manually:

```bash
curl -s -X POST http://127.0.0.1:8000/log \
  -H "Content-Type: application/json" \
  -d '{"user_id":"live_demo","event_type":"login","location":"Russia","device":"Unknown Device","source_ip":"185.200.10.15"}' | python3 -m json.tool
```

**Say:**
> "Rule scoring adds 40 for Russia, 40 for unknown device — base 20, total rule risk 100. Hybrid detection runs Isolation Forest on a 4-feature vector: login hour, elevated risk count, event frequency, and risk score. Baseline service checks deviation from the user's normal profile before updating it."

**Point out in response:**
- `rule_risk_score`: 100
- `hybrid_risk_score`: composite score
- `ml_anomaly`: true/false
- `baseline_deviation`: true/false
- `confidence`: hybrid engine confidence
- `threat_intel`: IOC match when IP/location in feed
- `ml_explanation`: SHAP top factors (when ML flags)

---

## Segment 3: Dashboard & Real-Time Monitoring (1:30)

**Do:** Switch to `http://localhost:3000`.

**Say:**
> "The React dashboard polls every 5 seconds. AuthContext manages JWT — in dev mode auth is optional; Docker deployment sets AUTH_REQUIRED=true."

**Show:**
1. **Metric cards** — logs, alerts, anomalies, avg risk
2. **Hybrid ML row** — ML anomalies, baseline deviations, detection rate, confidence
3. **Risk Distribution donut** — LOW/MEDIUM/HIGH/CRITICAL buckets
4. **Live Security Feed** — real-time event stream

**Do:** Start log generator in background:
```bash
MAX_LOGS=0 LOG_INTERVAL=3 python3 log_generator.py
```

**Expected:** Feed updates within 5 seconds; toast notifications on errors only.

---

## Segment 4: Hybrid ML & Baselines (1:30)

**Say:**
> "Isolation Forest is trained offline via `train_ml_model.py`, stored as pickle with path allowlisting. The hybrid engine combines three signals: rule anomalies, ML outliers, and baseline deviations. Confidence is clamped to [0,1] to prevent score inflation."

**Show:** Analytics view (sidebar → Analytics):
- Risk Trend Chart
- ML Anomaly Trend
- Baseline Deviation Trend

**Expected:** Charts render with data points from demo users.

---

## Segment 5: Threat Intelligence (1:00)

**Do:** Sidebar → **Threat Intel**

**Say:**
> "Threat intel supports JSON, CSV, or mock feeds via environment variables. IOCs are cached in memory. Enrichment happens at ingestion time — matching source IP or location against the feed."

**Show:** Panel metrics — 17 IOCs, malicious/suspicious breakdown, category chart.

**Do:** API call:
```bash
curl -s http://127.0.0.1:8000/threat-intel/ip/185.200.10.15 | python3 -m json.tool
```

**Expected:** `threat_score: 95`, `category: Botnet`, human-readable context string.

---

## Segment 6: Correlation Engine (1:30)

**Do:** Sidebar → **Correlation**

**Say:**
> "Four attack chain rules run after every log ingestion, scoped per user_id:
> 1. Credential Stuffing — fail, fail, success within 2 hours
> 2. Account Takeover — new device, high risk, privileged access (requires established baseline)
> 3. Insider Threat — 5+ high-risk events in 24 hours
> 4. Impossible Travel — 2+ locations within 2 hours"

**Show:** Alerts for `demo_stuff`, `demo_travel`, `demo_takeover`, `demo_insider`.

**Do:** Click a correlation alert detail (if UI supports) or:
```bash
curl -s http://127.0.0.1:8000/correlation-alerts/1 | python3 -m json.tool
```

**Expected:** Timeline of correlated events, recommended SOC action.

---

## Segment 7: Explainable AI (1:00)

**Do:** Sidebar → **Explainability**

**Say:**
> "SHAP TreeExplainer provides feature attribution for Isolation Forest decisions. Falls back to deviation-based explanation if model unavailable. First call is ~1 second; subsequent calls are cached."

**Show:** Top factors with feature names and contribution values; summary text.

**Expected:** Factors like `risk_score`, `login_hour`, `event_frequency`.

---

## Segment 8: Auth, RBAC & Investigation (1:00)

**Do:** If login page visible — sign in `admin` / `Admin123!`. Otherwise note guest mode.

**Say:**
> "JWT with bcrypt passwords. Three roles: ADMIN (full access), ANALYST (analytics + investigation), VIEWER (dashboard only). RBAC enforced via FastAPI dependencies."

**Do:** Sidebar → **Investigation** → select alert.

**Show:**
- MITRE ATT&CK technique mapping (T1078, T1110, etc.)
- Alert severity and description
- Incident report endpoint available at `/incident-report/{id}`

---

## Segment 9: Close & Q&A Bridge (30 sec)

**Say:**
> "32 unit tests pass. Docker Compose deploys both services. Known production gaps: pickle deserialization should migrate to ONNX, and rate limiting on POST /log. The v1.0.1 patch fixed threat feed parsing and account takeover false positives for new users."

**Offer:** "I can walk through the correlation rule code, ML training pipeline, or Docker deployment — whichever interests you most."

---

## Technical Demo Timing

| Segment | Duration | Focus |
|---------|----------|-------|
| Architecture | 1:30 | API docs, pipeline |
| Ingestion | 1:30 | curl POST /log response |
| Dashboard | 1:30 | Live feed, metrics |
| Hybrid ML | 1:30 | Analytics charts |
| Threat Intel | 1:00 | IOC panel + API |
| Correlation | 1:30 | Attack chains |
| SHAP | 1:00 | Explainability |
| Auth/Investigation | 1:00 | MITRE, RBAC |
| Close | 0:30 | Tests, Docker |

---

## Commands Cheat Sheet

```bash
# Health
curl http://127.0.0.1:8000/health

# Login
curl -s -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}'

# Analytics snapshot
curl -s http://127.0.0.1:8000/analytics | python3 -c "import sys,json; d=json.load(sys.stdin); print('anomalies:', d['anomaly_stats']['total_anomalies'], 'correlations:', d['correlation_alerts']['total'])"

# Live generator
MAX_LOGS=0 LOG_INTERVAL=3 python3 log_generator.py
```
