import logging

from app.database.database import get_connection
from app.services.anomaly_service import evaluate_rule_anomaly
from app.services.ml_anomaly_service import detect_ml_anomaly
from app.services.baseline_service import check_baseline_deviation

logger = logging.getLogger(__name__)


def _safe_unit_interval(value, default=0.0):
    """Coerce a value to a float clamped to [0.0, 1.0]. None/invalid/NaN → default."""
    if value is None:
        return default
    try:
        num = float(value)
    except (TypeError, ValueError):
        return default
    if num != num:  # NaN
        return default
    return max(0.0, min(num, 1.0))


def calculate_confidence(rule_anomaly, ml_anomaly, baseline_deviation, rule_score, ml_score, deviation_score=0):
    """
    Compute hybrid detection confidence from all signals.
    Output is always clamped to [0.0, 1.0].
    """
    confidence = 0.0

    if rule_anomaly:
        if rule_score is not None and rule_score <= 1:
            confidence += 0.45 * _safe_unit_interval(rule_score)
        else:
            confidence += 0.45 * _safe_unit_interval((rule_score or 0) / 100.0)

    if ml_anomaly:
        confidence += 0.35 * _safe_unit_interval(ml_score)

    if baseline_deviation:
        dev_ratio = _safe_unit_interval((deviation_score or 0) / 30.0)
        confidence += 0.20 * dev_ratio

    return round(_safe_unit_interval(confidence), 2)


def run_hybrid_detection(user_id, risk_score, login_hour, location, device, conn=None, log_id=None):
    """
    Combine rule-based, ML, and baseline detection into a unified result.

    Baseline sequence (P0 fix): check_baseline_deviation() runs BEFORE any
    baseline update in main.py. ML failures degrade gracefully to rule-only.
    """
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    rule_result = evaluate_rule_anomaly(user_id, risk_score, conn=conn)

    try:
        ml_result = detect_ml_anomaly(
            user_id, risk_score, login_hour, conn=conn, exclude_log_id=log_id
        )
    except Exception as exc:
        logger.error("ML layer failed, degrading to rule-only: %s", exc)
        ml_result = {
            "ml_anomaly": False,
            "anomaly_score": 0.0,
            "ml_score": 0.0,
            "model_ready": False,
        }

    baseline_result = check_baseline_deviation(
        user_id, login_hour, location, device, conn=conn, exclude_log_id=log_id
    )

    rule_anomaly = rule_result["anomaly_detected"]
    ml_anomaly = ml_result["ml_anomaly"]
    baseline_deviation = baseline_result["baseline_deviation"]

    hybrid_anomaly = rule_anomaly or ml_anomaly or baseline_deviation

    rule_score = rule_result["anomaly_score"]
    ml_score = ml_result.get("ml_score")
    if ml_score is None:
        ml_score = ml_result.get("anomaly_score", 0) or 0

    confidence = calculate_confidence(
        rule_anomaly, ml_anomaly, baseline_deviation, rule_score, ml_score,
        baseline_result.get("deviation_score", 0),
    )

    anomaly_type = rule_result["anomaly_type"]
    if hybrid_anomaly and not anomaly_type:
        if ml_anomaly:
            anomaly_type = "ML Outlier"
        elif baseline_deviation:
            anomaly_type = "Baseline Deviation"

    if rule_anomaly and ml_anomaly:
        anomaly_type = "Hybrid Detection"

    combined_score = max(rule_score, ml_score)
    if baseline_deviation:
        combined_score = max(combined_score, 0.75)

    if hybrid_anomaly:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO anomalies (
                user_id, risk_score, anomaly_score, anomaly_type,
                ml_anomaly, ml_score, baseline_deviation, confidence_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            risk_score,
            combined_score,
            anomaly_type,
            int(ml_anomaly),
            ml_score,
            int(baseline_deviation),
            confidence,
        ))
        conn.commit()
        logger.info(
            "Hybrid anomaly user=%s rule=%s ml=%s baseline=%s confidence=%.2f",
            user_id, rule_anomaly, ml_anomaly, baseline_deviation, confidence,
        )

    if close_conn:
        conn.close()

    return {
        "rule_anomaly": rule_anomaly,
        "ml_anomaly": ml_anomaly,
        "baseline_deviation": baseline_deviation,
        "anomaly": hybrid_anomaly,
        "confidence": confidence,
        "anomaly_detected": hybrid_anomaly,
        "anomaly_score": combined_score if hybrid_anomaly else 0.0,
        "anomaly_type": anomaly_type,
        "baseline_reason": baseline_result.get("reason"),
        "ml_model": ml_result.get("model"),
        "ml_score": ml_score,
        "deviation_score": baseline_result.get("deviation_score", 0),
    }
