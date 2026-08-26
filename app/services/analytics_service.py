from app.database.database import get_connection
from app.services.anomaly_service import get_anomaly_stats
from app.services.ml_anomaly_service import get_ml_anomaly_stats
from app.services.threat_intelligence_service import get_threat_intel_summary
from app.services.correlation_engine import get_correlation_alerts
from app.services.explainable_ml_service import explain_latest_ml_anomaly

# Effective hybrid score: explicit column with fallback for pre-12.1 rows
_HYBRID_SCORE_SQL = "COALESCE(hybrid_risk_score, risk_score)"


def get_analytics_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT AVG({_HYBRID_SCORE_SQL})
        FROM security_logs
    """)
    avg_hybrid_risk = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT AVG(rule_risk_score)
        FROM security_logs
        WHERE rule_risk_score IS NOT NULL
    """)
    avg_rule_risk = cursor.fetchone()[0] or 0

    cursor.execute(f"""
        SELECT user_id,
               SUM({_HYBRID_SCORE_SQL}) as total_risk
        FROM security_logs
        GROUP BY user_id
        ORDER BY total_risk DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    most_targeted_user = row[0] if row else "N/A"

    cursor.execute(f"""
        SELECT user_id,
               SUM({_HYBRID_SCORE_SQL}) as total_risk
        FROM security_logs
        GROUP BY user_id
        ORDER BY total_risk DESC
        LIMIT 5
    """)
    users = cursor.fetchall()

    trend_data = [
        {"user": user[0], "risk_score": user[1]}
        for user in users
    ]

    cursor.execute("SELECT COUNT(*) FROM alerts")
    total_alerts = cursor.fetchone()[0]

    conn.close()

    anomaly_stats = get_anomaly_stats()
    ml_stats = get_ml_anomaly_stats()
    threat_intel = get_threat_intel_summary()
    correlation = get_correlation_alerts(limit=20)
    ml_explanation = explain_latest_ml_anomaly()

    hybrid_rate = 0.0
    if anomaly_stats["total_anomalies"] > 0:
        hybrid_rate = round(
            (anomaly_stats.get("hybrid_detection_count", 0) / anomaly_stats["total_anomalies"]) * 100,
            1,
        )

    return {
        # average_risk preserved for backward compatibility (= hybrid average)
        "average_risk": round(avg_hybrid_risk, 2),
        "average_hybrid_risk": round(avg_hybrid_risk, 2),
        "average_rule_risk": round(avg_rule_risk, 2),
        "most_targeted_user": most_targeted_user,
        "total_alerts": total_alerts,
        "trend_data": trend_data,
        "anomaly_stats": anomaly_stats,
        "ml_stats": ml_stats,
        "hybrid_stats": {
            "ml_anomalies": anomaly_stats.get("ml_anomalies", 0),
            "baseline_deviations": anomaly_stats.get("baseline_deviations", 0),
            "hybrid_detection_rate": hybrid_rate,
            "average_confidence": anomaly_stats.get("average_confidence", 0),
        },
        "threat_intel": threat_intel,
        "correlation_alerts": correlation,
        "ml_explanation": ml_explanation,
    }
