from app.database.database import get_connection

_HYBRID_SCORE_SQL = "COALESCE(hybrid_risk_score, risk_score)"


def get_realtime_dashboard():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT
            user_id,
            event_type,
            {_HYBRID_SCORE_SQL} AS hybrid_score,
            rule_risk_score,
            timestamp
        FROM security_logs
        ORDER BY id DESC
    """)

    logs = cursor.fetchall()

    total_logs = len(logs)

    high_risk = 0
    medium_risk = 0
    low_risk = 0

    latest_events = []

    for log in logs:
        hybrid_score = log[2] or 0

        if hybrid_score >= 80:
            high_risk += 1
        elif hybrid_score >= 50:
            medium_risk += 1
        else:
            low_risk += 1

    for log in logs[:10]:
        hybrid_score = log[2] or 0
        latest_events.append(
            {
                "user_id": log[0],
                "event_type": log[1],
                # risk_score kept as hybrid for backward-compatible clients
                "risk_score": hybrid_score,
                "hybrid_risk_score": hybrid_score,
                "rule_risk_score": log[3],
                "timestamp": log[4],
            }
        )

    conn.close()

    return {
        "total_logs": total_logs,
        "high_risk_events": high_risk,
        "medium_risk_events": medium_risk,
        "low_risk_events": low_risk,
        "latest_events": latest_events,
    }
