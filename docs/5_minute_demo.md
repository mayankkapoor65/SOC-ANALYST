# 5-Minute Demo Walkthrough

**Audience:** General interviewers, hiring managers, non-technical stakeholders  
**Goal:** Show the product works end-to-end in under 5 minutes

---

## Before You Start (30 seconds)

1. Backend running on port 8000
2. Frontend open at `http://localhost:3000`
3. Demo data loaded (`sample_data/demo_logs.json` — see [demo_checklist.md](demo_checklist.md))

---

## Minute 0:00 — Opening (30 sec)

**Say:**
> "This is SentinelAI — a Mini-SIEM I built for real-time security log analysis. It ingests login events, scores risk using rules and machine learning, correlates attack chains, and presents everything on a SOC-style dashboard."

**Show:** Dashboard home — point to the four metric cards (Total Logs, Alerts, Anomalies, Average Risk).

---

## Minute 0:30 — Live Ingestion (45 sec)

**Do:** Open Terminal with log generator running (or run one manual POST):

```bash
MAX_LOGS=5 LOG_INTERVAL=1 python3 log_generator.py
```

**Say:**
> "Events flow in through a REST API. Each log gets a rule-based risk score, then passes through a hybrid ML engine with Isolation Forest and behavioral baselines."

**Show:** Live Security Feed updating with new events and risk scores.

**Expected:** New rows appear; some show elevated risk (Russia/Unknown Device → risk 100).

---

## Minute 1:15 — Threat Detection (45 sec)

**Do:** Point to the dashboard panels — Risk Distribution donut, AI Insights widget.

**Say:**
> "High-risk locations like Russia and China add 40 points. Unknown devices add another 40. When hybrid risk exceeds 80, the system auto-generates alerts mapped to MITRE ATT&CK techniques."

**Show:** Click **Alerts** in sidebar → show HIGH/CRITICAL alerts for `demo_ml` or similar users.

**Expected:** Alert list with severity badges and user IDs.

---

## Minute 2:00 — Threat Intelligence (45 sec)

**Do:** Click **Threat Intel** in sidebar.

**Say:**
> "Every event is enriched against a local IOC feed — 17 indicators covering botnets, scanners, and high-risk geographies. We match by IP or location."

**Show:** Threat Intel panel — total IOCs, malicious count, category breakdown.

**Expected:** `total_iocs: 17`, categories include Botnet, Scanner, Malicious.

---

## Minute 2:45 — Correlation Engine (45 sec)

**Do:** Click **Correlation** in sidebar.

**Say:**
> "Individual alerts aren't enough — the correlation engine chains events into attack patterns: credential stuffing, account takeover, impossible travel, and insider threats."

**Show:** Point to alerts for `demo_stuff` (Credential Stuffing), `demo_travel` (Impossible Travel), `demo_takeover` (Account Takeover).

**Expected:** At least 3 correlation alert types visible with confidence scores.

---

## Minute 3:30 — Explainable AI (45 sec)

**Do:** Click **Explainability** in sidebar.

**Say:**
> "When the ML model flags an anomaly, SHAP explains why — which features drove the decision. This is critical for SOC analyst trust and audit compliance."

**Show:** Top factors (login hour, risk score, event frequency) and natural-language summary.

**Expected:** SHAP method shown with 3–4 top contributing factors.

---

## Minute 4:15 — Investigation & Close (45 sec)

**Do:** Click **Investigation** → select any HIGH alert.

**Say:**
> "Analysts get a full investigation view with MITRE mapping, recommended actions, and incident report generation. The platform supports JWT authentication with role-based access — Admin, Analyst, and Viewer."

**Show:** MITRE technique ID (e.g., T1078 Valid Accounts), recommended action text.

**Close:**
> "The full stack is FastAPI, SQLite, scikit-learn, and React — containerized with Docker. Happy to dive deeper into any component."

---

## Timing Summary

| Time | Section | Key Visual |
|------|---------|------------|
| 0:00 | Intro | Metric cards |
| 0:30 | Live ingestion | Live Security Feed |
| 1:15 | Detection | Alerts panel |
| 2:00 | Threat Intel | IOC summary |
| 2:45 | Correlation | Attack chain alerts |
| 3:30 | SHAP | Top factors |
| 4:15 | Investigation | MITRE mapping |

---

## Backup If Live Feed Is Slow

Skip log generator; rely on pre-loaded `demo_logs.json` data. All panels still populate from existing database records.
