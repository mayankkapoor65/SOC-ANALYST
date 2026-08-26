import logging

from app.database.database import get_connection
from app.services.mitre_mapping_service import get_recommended_action, map_to_mitre

logger = logging.getLogger(__name__)


def _fetch_alert(alert_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, severity, description, timestamp,
               source_ip, mitre_technique_id, mitre_technique_name
        FROM alerts WHERE id = ?
        """,
        (alert_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def _fetch_user_logs(user_id, timestamp, limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, event_type, location, device, risk_score, anomaly_status,
               timestamp, ml_anomaly, baseline_deviation, rule_risk_score
        FROM security_logs
        WHERE user_id = ?
        ORDER BY ABS(julianday(timestamp) - julianday(?)) ASC
        LIMIT ?
        """,
        (user_id, timestamp, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def _fetch_user_anomalies(user_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT anomaly_type, anomaly_score, ml_anomaly, baseline_deviation,
               confidence_score, created_at
        FROM anomalies
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_investigation(alert_id: int):
    """Build full investigation view for a given alert."""
    alert = _fetch_alert(alert_id)
    if not alert:
        return None

    alert_id, user_id, severity, description, timestamp, source_ip, stored_tid, stored_tname = alert

    logs = _fetch_user_logs(user_id, timestamp)
    anomalies = _fetch_user_anomalies(user_id)

    primary_log = logs[0] if logs else None
    anomaly_type = None
    risk_score = 0
    ml_anomaly = False
    baseline_deviation = False

    if primary_log:
        risk_score = primary_log[4] or 0
        ml_anomaly = bool(primary_log[7])
        baseline_deviation = bool(primary_log[8])
        event_type = primary_log[1]
    else:
        event_type = "unknown"

    if anomalies:
        anomaly_type = anomalies[0][0]

    if stored_tid and stored_tname:
        mitre = {"technique_id": stored_tid, "technique_name": stored_tname}
    else:
        mitre = map_to_mitre(
            anomaly_type=anomaly_type,
            event_type=event_type,
            description=description,
            risk_score=risk_score,
            baseline_deviation=baseline_deviation,
            ml_anomaly=ml_anomaly,
        )

    timeline = []
    for log in logs[:10]:
        timeline.append({
            "timestamp": log[6],
            "event": log[1],
            "location": log[2],
            "device": log[3],
            "risk_score": log[4],
            "status": log[5],
        })

    evidence = []
    for log in logs[:5]:
        if (log[4] or 0) >= 50 or log[5] == "ANOMALY":
            evidence.append({
                "log_id": log[0],
                "event_type": log[1],
                "location": log[2],
                "device": log[3],
                "risk_score": log[4],
                "rule_risk_score": log[9],
                "timestamp": log[6],
                "ml_anomaly": bool(log[7]),
                "baseline_deviation": bool(log[8]),
            })

    for anomaly in anomalies[:3]:
        evidence.append({
            "type": "anomaly",
            "anomaly_type": anomaly[0],
            "anomaly_score": anomaly[1],
            "confidence": anomaly[4],
            "timestamp": anomaly[5],
        })

    recommended = get_recommended_action(mitre, severity, risk_score)

    return {
        "alert_id": alert_id,
        "alert": {
            "id": alert_id,
            "severity": severity,
            "description": description,
            "timestamp": timestamp,
        },
        "severity": severity,
        "user": user_id,
        "source_ip": source_ip or (primary_log[2] if primary_log else "Unknown"),
        "timeline": timeline,
        "evidence": evidence,
        "risk_score": risk_score,
        "mitre_mapping": mitre,
        "recommended_action": recommended,
    }


def get_all_alerts(limit=50):
    """Return alerts list for dashboard investigation panel."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, severity, description, timestamp, source_ip,
               mitre_technique_id, mitre_technique_name
        FROM alerts
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    return {
        "alerts": [
            {
                "id": row[0],
                "user_id": row[1],
                "severity": row[2],
                "description": row[3],
                "timestamp": row[4],
                "source_ip": row[5],
                "mitre_technique_id": row[6],
                "mitre_technique_name": row[7],
            }
            for row in rows
        ],
        "total": len(rows),
    }
