"""
Explainable ML Service — SHAP-based feature impact analysis for Isolation Forest anomalies.
"""

import logging

import numpy as np

from app.database.database import get_connection
from app.services.ml_anomaly_service import (
    extract_features,
    load_model,
    load_scaler,
    FEATURE_NAMES,
)

logger = logging.getLogger(__name__)

FEATURE_LABELS = {
    "login_hour": "login hour",
    "elevated_risk_count": "elevated risk event count",
    "event_frequency": "event frequency",
    "risk_score": "rule risk score",
}


def _fallback_explanation(features: dict, anomaly_score: float) -> dict:
    """Deviation-based explanation when SHAP unavailable."""
    impacts = []
    baseline = {"login_hour": 12, "elevated_risk_count": 0, "event_frequency": 1, "risk_score": 20}

    for feat in FEATURE_NAMES:
        val = features.get(feat, 0) or 0
        base = baseline.get(feat, 0)
        diff = abs(val - base)
        max_diff = max(abs(val), abs(base), 1)
        impact = round(min(diff / max_diff, 1.0) * 0.5, 2)
        if impact > 0.05:
            impacts.append({"feature": feat, "impact": impact})

    impacts.sort(key=lambda x: x["impact"], reverse=True)
    if not impacts:
        impacts = [{"feature": "risk_score", "impact": round(anomaly_score * 0.5, 2)}]

    return {
        "anomaly_score": anomaly_score,
        "top_factors": impacts[:4],
        "method": "deviation_fallback",
    }


def _compute_shap_impacts(scaled_vector, model) -> list:
    """Compute SHAP values using TreeExplainer."""
    import shap

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(scaled_vector)

    if isinstance(shap_values, list):
        values = shap_values[0][0] if len(shap_values) > 0 else shap_values[0]
    else:
        values = shap_values[0]

    abs_values = np.abs(values)
    total = abs_values.sum() or 1.0

    impacts = []
    for i, feat in enumerate(FEATURE_NAMES):
        impacts.append({
            "feature": feat,
            "impact": round(float(abs_values[i] / total), 2),
        })

    impacts.sort(key=lambda x: x["impact"], reverse=True)
    return impacts[:4]


def generate_explanation_summary(top_factors: list, log_row: dict) -> str:
    """Build human-readable explanation from top SHAP factors."""
    if not top_factors:
        return "This event was flagged by the ML model based on an unusual feature combination."

    parts = []
    for factor in top_factors[:3]:
        feat = factor["feature"]
        label = FEATURE_LABELS.get(feat, feat.replace("_", " "))
        val = log_row.get(feat)

        if feat == "login_hour" and val is not None:
            parts.append(f"login occurred at an unusual hour ({val}:00)")
        elif feat == "event_frequency" and val is not None:
            parts.append(f"abnormal event frequency ({val} events in the last hour)")
        elif feat == "elevated_risk_count" and val is not None:
            parts.append(f"elevated prior risk events ({val} high-risk events)")
        elif feat == "risk_score" and val is not None:
            parts.append(f"elevated rule risk score ({val})")
        else:
            parts.append(f"unusual {label}")

    if len(parts) == 1:
        return f"This event was flagged because {parts[0]}."
    return f"This event was flagged because {', '.join(parts[:-1])}, and {parts[-1]}."


def explain_log(log_id: int):
    """Generate ML explanation for a specific log entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, risk_score, rule_risk_score, login_hour, ml_anomaly, ml_score,
               location, device, timestamp
        FROM security_logs WHERE id = ?
    """, (log_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    log_id, user_id, risk_score, rule_risk_score, login_hour, ml_anomaly, ml_score, location, device, timestamp = row
    rule_score = rule_risk_score or risk_score or 20
    hour = login_hour if login_hour is not None else 12
    anomaly_score = float(ml_score or 0)

    features = extract_features(user_id, rule_score, hour, exclude_log_id=log_id)
    feature_dict = {
        "login_hour": features["login_hour"],
        "elevated_risk_count": features["elevated_risk_count"],
        "event_frequency": features["event_frequency"],
        "risk_score": features["risk_score"],
    }

    model = load_model()
    scaler = load_scaler()

    if model is None or scaler is None or not ml_anomaly:
        fallback = _fallback_explanation(feature_dict, anomaly_score)
        summary = generate_explanation_summary(fallback["top_factors"], feature_dict)
        return {
            **fallback,
            "log_id": log_id,
            "user_id": user_id,
            "ml_anomaly": bool(ml_anomaly),
            "explanation_summary": summary,
        }

    try:
        scaled = scaler.transform(features["vector"])
        top_factors = _compute_shap_impacts(scaled, model)
        summary = generate_explanation_summary(top_factors, feature_dict)
        return {
            "log_id": log_id,
            "user_id": user_id,
            "anomaly_score": anomaly_score,
            "ml_anomaly": bool(ml_anomaly),
            "top_factors": top_factors,
            "explanation_summary": summary,
            "method": "shap",
            "features": feature_dict,
        }
    except Exception as exc:
        logger.error("SHAP explanation failed for log_id=%s: %s", log_id, exc)
        fallback = _fallback_explanation(feature_dict, anomaly_score)
        summary = generate_explanation_summary(fallback["top_factors"], feature_dict)
        return {
            **fallback,
            "log_id": log_id,
            "user_id": user_id,
            "ml_anomaly": bool(ml_anomaly),
            "explanation_summary": summary,
        }


def explain_latest_ml_anomaly():
    """Return explanation for the most recent ML-flagged log."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM security_logs
        WHERE ml_anomaly = 1
        ORDER BY id DESC LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return explain_log(row[0])
