# Phase 15 — Explainable ML (SHAP)

## Architecture

The Explainable ML Service (`app/services/explainable_ml_service.py`) uses SHAP TreeExplainer to explain Isolation Forest anomaly decisions, with a deviation-based fallback when SHAP is unavailable.

```
ML Anomaly Detected → extract_features → SHAP TreeExplainer → top_factors + summary
```

## Features Analyzed

| Feature | Description |
|---------|-------------|
| login_hour | Hour of login (0–23) |
| elevated_risk_count | Prior high-risk events for user |
| event_frequency | Events in last hour |
| risk_score | Rule-engine risk score |

## API Endpoints

| Method | Path | Response |
|--------|------|----------|
| GET | `/ml-explanation/{log_id}` | anomaly_score, top_factors, explanation_summary |

POST /log also returns additive `ml_explanation` field when ML anomaly is detected.

## Response Format

```json
{
  "log_id": 42,
  "anomaly_score": 0.91,
  "top_factors": [
    {"feature": "login_hour", "impact": 0.42},
    {"feature": "event_frequency", "impact": 0.28}
  ],
  "explanation_summary": "This event was flagged because login occurred at an unusual hour (3:00), and abnormal event frequency (8 events in the last hour).",
  "method": "shap"
}
```

## Dashboard Components

- **ExplainabilityPanel** — AI summary, horizontal bar chart of feature impacts
- Embedded on main dashboard and dedicated Explainable AI view

## Use Cases

- SOC analyst understanding of ML false positives
- Compliance/audit trail for automated decisions
- Portfolio demonstration of responsible AI in security
