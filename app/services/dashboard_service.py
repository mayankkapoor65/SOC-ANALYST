from app.database.database import get_connection


def get_dashboard_summary():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM security_logs"
    )
    total_logs = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM security_logs
        WHERE status='ANOMALY'
        """
    )
    total_anomalies = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM security_logs
        WHERE status='NORMAL'
        """
    )
    total_normal = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM alerts"
    )
    total_alerts = cursor.fetchone()[0]

    conn.close()

    return {
        "total_logs": total_logs,
        "total_alerts": total_alerts,
        "total_anomalies": total_anomalies,
        "total_normal": total_normal
    }


def get_severity_distribution():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT severity, COUNT(*)
        FROM alerts
        GROUP BY severity
    """)

    rows = cursor.fetchall()

    conn.close()

    result = {}

    for row in rows:
        result[row[0]] = row[1]

    return result


def get_top_risk_users():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            user_id,
            MAX(risk_score) as highest_risk
        FROM security_logs
        GROUP BY user_id
        ORDER BY highest_risk DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()

    conn.close()

    users = []

    for row in rows:
        users.append({
            "user_id": row[0],
            "highest_risk": row[1]
        })

    return users