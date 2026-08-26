# Phase 14 — SIEM Correlation Engine

## Architecture

The Correlation Engine (`app/services/correlation_engine.py`) detects multi-event attack chains by analyzing recent user activity after each log ingestion.

```
POST /log → Hybrid Detection → run_correlation_engine(user_id) → correlation_alerts table
```

## Detection Rules

| Rule | Pattern | Alert Type | Severity |
|------|---------|------------|----------|
| 1 | Failed Login → Failed Login → Successful Login | Credential Stuffing | HIGH |
| 2 | New Device → High Risk Login → Privileged Access | Account Takeover | CRITICAL |
| 3 | High-risk events ≥ 5 in 24h | Potential Insider Threat | HIGH |
| 4 | Multiple locations within 2 hours | Impossible Travel | HIGH |

## Data Model

**Table:** `correlation_alerts`

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER PK | Auto-increment |
| alert_type | TEXT | Alert classification |
| severity | TEXT | CRITICAL / HIGH |
| user_id | TEXT | Affected user |
| description | TEXT | Human-readable summary |
| confidence | REAL | 0.0–1.0 |
| created_at | TEXT | UTC timestamp |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/correlation-alerts` | List recent correlation alerts |
| GET | `/correlation-alerts/{id}` | Full detail with timeline, events, recommended action |

## Dashboard Components

- **CorrelationAlertsPanel** — Alert table, attack chain timeline, recommended actions
- Embedded on main dashboard and dedicated Correlation view

## Use Cases

- Detect credential stuffing campaigns across failed-then-success login patterns
- Identify account takeover via device + privilege escalation chains
- Flag insider threat behavior from sustained high-risk activity
- Detect impossible travel from geolocation velocity analysis
