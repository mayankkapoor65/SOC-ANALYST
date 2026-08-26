from app.database.database import get_connection


def get_threat_trends():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM security_logs
        WHERE status='ANOMALY'
    """)
    anomaly_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
    """)
    alert_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT AVG(risk_score)
        FROM security_logs
    """)
    avg_risk = cursor.fetchone()[0]

    cursor.execute("""
        SELECT MAX(risk_score)
        FROM security_logs
    """)
    max_risk = cursor.fetchone()[0]

    conn.close()

    return {
        "total_anomalies": anomaly_count,
        "total_alerts": alert_count,
        "average_risk_score": round(avg_risk or 0, 2),
        "highest_risk_score": max_risk or 0
    }