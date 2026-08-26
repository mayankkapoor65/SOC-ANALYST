import logging

from app.database.database import get_connection

logger = logging.getLogger(__name__)


def evaluate_rule_anomaly(user_id, risk_score, conn=None):
    """
    Evaluate rule-based anomaly without inserting.
    Used by hybrid detection engine.
    """
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(risk_score)
        FROM security_logs
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()
    historical_avg = result[0] if result and result[0] else 0

    anomaly_score = 0.0
    anomaly_type = None

    if risk_score >= 90:
        anomaly_score = 0.95
        anomaly_type = "High Risk Spike"
    elif historical_avg > 0 and risk_score > (historical_avg * 1.5):
        anomaly_score = 0.85
        anomaly_type = "Behavior Deviation"

    if close_conn:
        conn.close()

    return {
        "anomaly_detected": anomaly_type is not None,
        "anomaly_score": anomaly_score,
        "anomaly_type": anomaly_type,
    }


def detect_anomaly(user_id, risk_score):
    """
    Rule-based anomaly detection (legacy endpoint compatibility).
    - High risk score spikes
    - Compare against user's historical average
    """
    result = evaluate_rule_anomaly(user_id, risk_score)

    if result["anomaly_type"]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO anomalies (
                user_id,
                risk_score,
                anomaly_score,
                anomaly_type
            )
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            risk_score,
            result["anomaly_score"],
            result["anomaly_type"],
        ))
        conn.commit()
        conn.close()
        logger.info(
            "Anomaly detected for user=%s type=%s score=%.2f",
            user_id, result["anomaly_type"], result["anomaly_score"],
        )

    return result


def get_anomaly_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM anomalies")
    total_anomalies = cursor.fetchone()[0]

    cursor.execute("""
        SELECT anomaly_type, COUNT(*) as count
        FROM anomalies
        GROUP BY anomaly_type
    """)
    by_type = [
        {"type": row[0], "count": row[1]}
        for row in cursor.fetchall()
    ]

    cursor.execute("""
        SELECT user_id, anomaly_type, anomaly_score, created_at,
               ml_anomaly, ml_score, baseline_deviation, confidence_score
        FROM anomalies
        ORDER BY id DESC
        LIMIT 10
    """)
    recent = [
        {
            "user_id": row[0],
            "anomaly_type": row[1],
            "anomaly_score": row[2],
            "created_at": row[3],
            "ml_anomaly": bool(row[4]) if row[4] is not None else False,
            "ml_score": row[5],
            "baseline_deviation": bool(row[6]) if row[6] is not None else False,
            "confidence": row[7],
        }
        for row in cursor.fetchall()
    ]

    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE ml_anomaly = 1")
    ml_anomalies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE baseline_deviation = 1")
    baseline_deviations = cursor.fetchone()[0]

    cursor.execute("""
        SELECT AVG(confidence_score) FROM anomalies
        WHERE confidence_score IS NOT NULL
    """)
    avg_confidence = cursor.fetchone()[0] or 0.0

    cursor.execute("""
        SELECT COUNT(*) FROM anomalies
        WHERE ml_anomaly = 1 OR anomaly_type IN ('Hybrid Detection', 'ML Outlier')
    """)
    hybrid_count = cursor.fetchone()[0]

    conn.close()

    return {
        "total_anomalies": total_anomalies,
        "by_type": by_type,
        "recent_anomalies": recent,
        "ml_anomalies": ml_anomalies,
        "baseline_deviations": baseline_deviations,
        "hybrid_detection_count": hybrid_count,
        "average_confidence": round(avg_confidence, 2),
    }
