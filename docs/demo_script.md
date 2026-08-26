# Demo Script — SentinelAI Security Analytics

**Duration:** 8–12 minutes (flexible)  
**Presenter:** Pragna  
**Project:** Security Log Anomaly Detection v1.0.1

---

## Pre-Demo Checklist (5 min before)

1. Start backend: `python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload`
2. Start frontend: `cd frontend && npm start`
3. Load demo data:
   ```bash
   python3 -c "
   import json, requests
   for e in json.load(open('sample_data/demo_logs.json')):
       p = {k:v for k,v in e.items() if k in ('user_id','event_type','location','device','source_ip') and v}
       requests.post('http://127.0.0.1:8000/log', json=p)
   print('Done')
   "
   ```
4. Open browser: `http://localhost:3000`
5. Optional: `MAX_LOGS=0 LOG_INTERVAL=3 python3 log_generator.py` in a third terminal

---

## Demo Flow — Start to Finish

### STEP 1: Introduction (1 min)

**What to say:**
> "I built SentinelAI — a Mini-SIEM platform that ingests security logs, detects anomalies using rules plus machine learning, correlates multi-step attack chains, and presents analyst-ready intelligence on a real-time dashboard."

**What to show:** Dashboard loaded at `http://localhost:3000`

**Expected output:** SentinelAI header, metric cards with numbers > 0, sidebar navigation visible.

**What to click:** Nothing yet — let the audience see the full dashboard layout.

---

### STEP 2: Architecture Context (1 min)

**What to say:**
> "Events enter through a FastAPI REST API. Each log passes through rule-based risk scoring, hybrid ML detection with Isolation Forest, behavioral baseline checks, threat intelligence enrichment, and a correlation engine — all persisted in SQLite and served to this React dashboard."

**What to show:** Briefly open `http://127.0.0.1:8000/docs` in a tab (optional).

**Expected output:** Swagger UI showing POST /log, GET /analytics, GET /correlation-alerts.

**What to click:** Expand `POST /log` to show request schema (user_id, event_type, location, device, source_ip).

---

### STEP 3: Live Log Ingestion (1.5 min)

**What to say:**
> "Let me show live ingestion. The log generator simulates real authentication events — random users, locations, and devices."

**What to do:** Run in terminal:
```bash
MAX_LOGS=8 LOG_INTERVAL=1 python3 log_generator.py
```

**What to click:** Dashboard → scroll to **Live Security Feed**

**Expected output:**
- Terminal prints: `[N] Sent: Pragna | risk=20 | anomaly=False` (and some with risk=100)
- Feed updates within 5 seconds with new rows
- Risk scores color-coded in the feed

**What to say (while waiting):**
> "Russia and China add 40 risk points. Unknown devices add another 40. The hybrid engine then layers ML and baseline analysis on top."

---

### STEP 4: Risk Scoring & Alerts (1 min)

**What to click:** Sidebar → **Alerts**

**What to say:**
> "When hybrid risk exceeds 80, the system automatically creates alerts with MITRE ATT&CK technique mapping. This gives SOC analysts immediate context on what type of attack they're seeing."

**Expected output:**
- Alert list with HIGH or CRITICAL severity
- Users like `demo_ml`, `John`, or `demo_takeover`
- Descriptions mentioning risk scores

**What to click:** Click any alert row if investigation panel opens, or go to Investigation next.

---

### STEP 5: Anomaly Detection (45 sec)

**What to click:** Sidebar → **Anomalies** (or point to Anomaly Center on dashboard)

**What to say:**
> "Anomalies are detected three ways: rule-based thresholds, Isolation Forest ML outliers, and behavioral baseline deviations. The hybrid engine combines all three with a confidence score."

**Expected output:**
- Anomaly count > 0
- Breakdown by type (rule, ML, baseline)
- Recent anomaly list with user IDs and timestamps

---

### STEP 6: Threat Intelligence (1 min)

**What to click:** Sidebar → **Threat Intel**

**What to say:**
> "Every event is enriched against a local threat feed with 17 IOCs — botnet IPs, scanners, and high-risk geographies. We match on source IP or location name."

**Expected output:**
- Total IOCs: 17
- Malicious IPs: ~12
- Category breakdown: Botnet, Scanner, Malicious, Suspicious
- Average threat score displayed

**What to say:**
> "For example, IP 185.200.10.15 is a known botnet with threat score 95. When a log includes that IP, enrichment appears in the API response and dashboard."

---

### STEP 7: Correlation Engine (1.5 min)

**What to click:** Sidebar → **Correlation**

**What to say:**
> "Individual events aren't enough for SOC triage. The correlation engine chains events into attack patterns across four rules."

**Expected output — point to each:**

| Alert Type | Demo User | What Happened |
|------------|-----------|---------------|
| Credential Stuffing | `demo_stuff` | 2 failed logins → 1 success |
| Impossible Travel | `demo_travel` | USA → Russia → China in minutes |
| Account Takeover | `demo_takeover` | New device → high risk → admin access |
| Insider Threat | `demo_insider` | 5+ high-risk events in 24 hours |

**What to say:**
> "Each rule is scoped to a single user — attack chains never mix unrelated users. Duplicate alerts are suppressed within a one-hour window."

---

### STEP 8: Explainable AI (1 min)

**What to click:** Sidebar → **Explainability**

**What to say:**
> "Black-box ML isn't acceptable in security operations. SHAP explains which features drove each ML anomaly — login hour, event frequency, risk score — in plain language."

**Expected output:**
- Method: `shap`
- Top 3–4 contributing factors with values
- Natural-language summary (e.g., "login occurred at an unusual hour")

---

### STEP 9: Investigation Workflow (1 min)

**What to click:** Sidebar → **Investigation**

**What to say:**
> "Analysts get a structured investigation view with MITRE ATT&CK mapping, event timeline, and recommended remediation actions. Incident reports can be generated per alert."

**Expected output:**
- Alert list with MITRE technique IDs (T1078, T1110, etc.)
- Technique names (Valid Accounts, Brute Force)
- Recommended actions per alert type

---

### STEP 10: Authentication (30 sec — optional)

**What to say:**
> "The platform supports JWT authentication with three roles: Admin, Analyst, and Viewer. Docker deployment enforces auth by default."

**What to do:** If login page is visible, sign in with `admin` / `Admin123!`

**Expected output:** Dashboard reloads showing logged-in user in header/settings.

**Note:** With `AUTH_REQUIRED=false` (local dev), the dashboard loads directly as guest admin — mention this is intentional for development.

---

### STEP 11: Closing (30 sec)

**What to say:**
> "To summarize: SentinelAI provides log ingestion, hybrid detection, threat intel enrichment, attack chain correlation, explainable ML, and a full SOC dashboard — built with FastAPI, SQLite, scikit-learn, SHAP, and React. It's containerized with Docker and covered by 35 unit tests. Happy to dive into any component."

**What to show:** Return to main dashboard — all panels populated.

---

## Quick Reference: What Triggers What

| Demo User | Scenario | Trigger |
|-----------|----------|---------|
| `demo_alice` | Normal login | India + Laptop → risk 20 |
| `demo_stuff` | Credential Stuffing | failed, failed, login |
| `demo_travel` | Impossible Travel | USA → Russia → China |
| `demo_threat` | Threat Intel | source_ip 185.200.10.15 |
| `demo_ml` | ML Anomaly + Alert | Russia + Unknown Device |
| `demo_takeover` | Account Takeover | baseline → new device → high risk → admin |
| `demo_insider` | Insider Threat | 5× high-risk events |

---

## Emergency Fallbacks

| Issue | Action |
|-------|--------|
| Dashboard empty | Re-load `sample_data/demo_logs.json` |
| Backend down | `python3 -m uvicorn main:app --host 127.0.0.1 --port 8000` |
| No live feed movement | Run `log_generator.py` |
| SHAP empty | Refresh page; wait 2 seconds |
| Login not shown | Explain dev mode bypass; show `/login` via API docs |

---

## Related Documents

- [demo_checklist.md](demo_checklist.md) — Pre-demo verification
- [5_minute_demo.md](5_minute_demo.md) — Short version
- [10_minute_demo.md](10_minute_demo.md) — Technical deep dive
- [presentation_questions.md](presentation_questions.md) — Q&A prep
