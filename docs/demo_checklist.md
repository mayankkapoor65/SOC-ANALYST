# Demo Checklist

Use this checklist **30 minutes before** your presentation. Check each box in order.

---

## Pre-Demo Setup (T-30 min)

- [ ] **Terminal 1 — Backend running**
  ```bash
  cd /Users/pragna/Desktop/Security-Log-Anomaly-Detection
  python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
  ```
  Verify: `curl http://127.0.0.1:8000/health` → `{"status":"healthy","database":"connected"}`

- [ ] **Terminal 2 — Frontend running**
  ```bash
  cd frontend
  npm start
  ```
  Verify: Browser opens at `http://localhost:3000`

- [ ] **Load demo dataset** (one-time before demo)
  ```bash
  cd /Users/pragna/Desktop/Security-Log-Anomaly-Detection
  python3 -c "
  import json, requests
  logs = json.load(open('sample_data/demo_logs.json'))
  for e in logs:
      p = {k:v for k,v in e.items() if k in ('user_id','event_type','location','device','source_ip') and v}
      r = requests.post('http://127.0.0.1:8000/log', json=p)
      print(e.get('description','')[:50], '→', r.status_code)
  "
  ```

- [ ] **Optional — Live log stream** (run during demo for movement)
  ```bash
  MAX_LOGS=0 LOG_INTERVAL=3 python3 log_generator.py
  ```

---

## Functional Checks (T-15 min)

- [ ] **Backend running** — `GET /health` returns 200
- [ ] **Frontend running** — Dashboard visible at `http://localhost:3000`
- [ ] **Login works** — `admin` / `Admin123!` (or skip if `AUTH_REQUIRED=false`)
- [ ] **Dashboard loads** — Metrics, charts, live feed visible; no red error screen
- [ ] **Threat Intel panel works** — Sidebar → Threat Intel OR visible on main dashboard; shows IOC counts
- [ ] **Correlation panel works** — Sidebar → Correlation; shows Credential Stuffing, Impossible Travel, etc.
- [ ] **Explainable AI panel works** — Sidebar → Explainability; shows SHAP top factors
- [ ] **Investigation panel works** — Sidebar → Investigation; shows alerts with MITRE technique IDs

---

## Data Presence Checks

- [ ] **Normal events** — Live feed shows `demo_alice`, `demo_bob` with low risk
- [ ] **High-risk events** — `demo_ml`, `demo_eve` with Russia/Unknown Device (risk 60–100)
- [ ] **Anomalies** — Anomaly Center or metrics show anomaly count > 0
- [ ] **Threat intel matches** — Threat Intel panel shows malicious IPs / categories
- [ ] **Correlation alerts** — At least: Credential Stuffing, Impossible Travel, Account Takeover
- [ ] **SHAP explanations** — Explainability panel shows top factors (login hour, risk score, etc.)

---

## Presentation Day Quick Reference

| Item | Value |
|------|-------|
| Backend URL | `http://127.0.0.1:8000` |
| Frontend URL | `http://localhost:3000` |
| Login | `admin` / `Admin123!` |
| API docs | `http://127.0.0.1:8000/docs` |
| Demo data file | `sample_data/demo_logs.json` |
| Live generator | `python3 log_generator.py` |

---

## If Something Breaks

| Problem | Fix |
|---------|-----|
| "Connection Failed" on dashboard | Restart backend; confirm port 8000 free |
| Empty panels | Re-run demo_logs.json loader (see above) |
| Login page not shown | Normal with `AUTH_REQUIRED=false`; dashboard loads as guest admin |
| SHAP panel empty | Wait 2s and refresh; ensure `models/isolation_forest.pkl` exists |
| No correlation alerts | Re-load demo_logs.json; check `/correlation-alerts` API |

---

**All boxes checked?** You are demo-ready. See [5_minute_demo.md](5_minute_demo.md) or [10_minute_demo.md](10_minute_demo.md) for walkthrough scripts.
