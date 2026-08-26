from app.database.database import get_connection


def get_security_metrics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT AVG(risk_score) FROM security_logs"
    )
    avg_risk = cursor.fetchone()[0]

    cursor.execute(
        "SELECT MAX(risk_score) FROM security_logs"
    )
    max_risk = cursor.fetchone()[0]

    cursor.execute(
        "SELECT MIN(risk_score) FROM security_logs"
    )
    min_risk = cursor.fetchone()[0]

    conn.close()

    return {
        "average_risk_score": round(avg_risk or 0, 2),
        "highest_risk_score": max_risk or 0,
        "lowest_risk_score": min_risk or 0
    }