"""
SIEM Correlation Engine — detect multi-event attack chains.
"""

import logging
from datetime import datetime, timedelta

from app.core.time_utils import utc_hours_ago_str
from app.database.database import get_connection

logger = logging.getLogger(__name__)

PRIVILEGED_EVENTS = {"admin", "privileged", "sudo", "root", "elevated"}
FAILED_EVENT_KEYWORDS = {"fail", "failed", "failure", "denied", "invalid"}
HIGH_RISK_THRESHOLD = 70
INSIDER_THREAT_COUNT = 5
IMPOSSIBLE_TRAVEL_HOURS = 2
IMPOSSIBLE_TRAVEL_MIN_LOCATIONS = 2


def _parse_ts(ts):
    if not ts:
        return None
    try:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def _is_failed(event_type: str) -> bool:
    et = (event_type or "").lower()
    return any(k in et for k in FAILED_EVENT_KEYWORDS)


def _is_success_login(event_type: str) -> bool:
    et = (event_type or "").lower()
    return "login" in et and not _is_failed(et)


def _is_privileged(event_type: str) -> bool:
    et = (event_type or "").lower()
    return any(p in et for p in PRIVILEGED_EVENTS)


def _is_new_device(device: str, typical_device: str) -> bool:
    if not device or not typical_device:
        return bool(device)
    return device != typical_device


def _get_user_baseline(user_id, conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT typical_device FROM user_baselines WHERE user_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    return row[0] if row else None


def _insert_correlation_alert(alert_type, severity, user_id, description, confidence, conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM correlation_alerts
        WHERE alert_type = ? AND user_id = ? AND created_at >= ?
        ORDER BY id DESC LIMIT 1
    """, (alert_type, user_id, utc_hours_ago_str(1)))
    if cursor.fetchone():
        return None

    cursor.execute("""
        INSERT INTO correlation_alerts (alert_type, severity, user_id, description, confidence)
        VALUES (?, ?, ?, ?, ?)
    """, (alert_type, severity, user_id, description, confidence))
    conn.commit()
    alert_id = cursor.lastrowid
    logger.info("Correlation alert created type=%s user=%s id=%s", alert_type, user_id, alert_id)
    return alert_id


def _fetch_recent_logs(user_id, hours=24, conn=None):
    close = False
    if conn is None:
        conn = get_connection()
        close = True

    cursor = conn.cursor()
    since = utc_hours_ago_str(hours)
    cursor.execute("""
        SELECT id, event_type, location, device, risk_score,
               COALESCE(hybrid_risk_score, risk_score) AS hybrid_score, timestamp
        FROM security_logs
        WHERE user_id = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    """, (user_id, since))
    rows = cursor.fetchall()

    if close:
        conn.close()

    return [
        {
            "id": r[0], "event_type": r[1], "location": r[2], "device": r[3],
            "risk_score": r[4], "hybrid_score": r[5] or 0, "timestamp": r[6],
        }
        for r in rows
    ]


def check_credential_stuffing(user_id, conn):
    logs = _fetch_recent_logs(user_id, hours=2, conn=conn)
    if len(logs) < 3:
        return None

    for i in range(len(logs) - 2):
        a, b, c = logs[i], logs[i + 1], logs[i + 2]
        if _is_failed(a["event_type"]) and _is_failed(b["event_type"]) and _is_success_login(c["event_type"]):
            return _insert_correlation_alert(
                "Credential Stuffing",
                "HIGH",
                user_id,
                "Failed login followed by failed login then successful login — possible credential stuffing.",
                0.85,
                conn,
            )
    return None


def check_account_takeover(user_id, conn):
    logs = _fetch_recent_logs(user_id, hours=4, conn=conn)
    if len(logs) < 3:
        return None

    typical = _get_user_baseline(user_id, conn)
    if not typical:
        return None

    for i in range(len(logs) - 2):
        a, b, c = logs[i], logs[i + 1], logs[i + 2]
        new_dev = _is_new_device(a["device"], typical)
        high_risk = (b["hybrid_score"] or 0) >= HIGH_RISK_THRESHOLD
        privileged = _is_privileged(c["event_type"])
        if new_dev and high_risk and privileged:
            return _insert_correlation_alert(
                "Account Takeover",
                "CRITICAL",
                user_id,
                "New device → high-risk login → privileged access detected.",
                0.90,
                conn,
            )
    return None


def check_insider_threat(user_id, conn):
    logs = _fetch_recent_logs(user_id, hours=24, conn=conn)
    high_risk = [l for l in logs if (l["hybrid_score"] or 0) >= HIGH_RISK_THRESHOLD]
    if len(high_risk) >= INSIDER_THREAT_COUNT:
        return _insert_correlation_alert(
            "Potential Insider Threat",
            "HIGH",
            user_id,
            f"{len(high_risk)} high-risk events in 24 hours exceeds threshold ({INSIDER_THREAT_COUNT}).",
            min(0.95, 0.6 + len(high_risk) * 0.05),
            conn,
        )
    return None


def check_impossible_travel(user_id, conn):
    logs = _fetch_recent_logs(user_id, hours=IMPOSSIBLE_TRAVEL_HOURS, conn=conn)
    if len(logs) < 2:
        return None

    locations = []
    timestamps = []
    for log in logs:
        if log["location"]:
            locations.append(log["location"])
            timestamps.append(_parse_ts(log["timestamp"]))

    unique_locs = set(locations)
    if len(unique_locs) < IMPOSSIBLE_TRAVEL_MIN_LOCATIONS:
        return None

    valid_ts = [t for t in timestamps if t]
    if len(valid_ts) >= 2:
        span = (max(valid_ts) - min(valid_ts)).total_seconds() / 3600
        if span <= IMPOSSIBLE_TRAVEL_HOURS:
            locs = ", ".join(sorted(unique_locs))
            return _insert_correlation_alert(
                "Impossible Travel",
                "HIGH",
                user_id,
                f"Logins from multiple locations ({locs}) within {IMPOSSIBLE_TRAVEL_HOURS} hours.",
                0.82,
                conn,
            )
    return None


def run_correlation_engine(user_id, conn=None):
    """Run all correlation rules for a user after log ingestion."""
    close = False
    if conn is None:
        conn = get_connection()
        close = True

    alerts_created = []
    for rule in (check_credential_stuffing, check_account_takeover, check_insider_threat, check_impossible_travel):
        try:
            alert_id = rule(user_id, conn)
            if alert_id:
                alerts_created.append(alert_id)
        except Exception as exc:
            logger.error("Correlation rule %s failed: %s", rule.__name__, exc)

    if close:
        conn.close()

    return alerts_created


def get_correlation_alerts(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, alert_type, severity, user_id, description, confidence, created_at
        FROM correlation_alerts
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    return {
        "alerts": [
            {
                "id": r[0], "alert_type": r[1], "severity": r[2],
                "user_id": r[3], "description": r[4],
                "confidence": r[5], "created_at": r[6],
            }
            for r in rows
        ],
        "total": len(rows),
    }


def get_correlation_alert_detail(alert_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, alert_type, severity, user_id, description, confidence, created_at
        FROM correlation_alerts WHERE id = ?
    """, (alert_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    alert = {
        "id": row[0], "alert_type": row[1], "severity": row[2],
        "user_id": row[3], "description": row[4],
        "confidence": row[5], "created_at": row[6],
    }

    events = _fetch_recent_logs(alert["user_id"], hours=24, conn=conn)
    conn.close()

    timeline = [
        {
            "timestamp": e["timestamp"],
            "event_type": e["event_type"],
            "location": e["location"],
            "device": e["device"],
            "risk_score": e["hybrid_score"],
        }
        for e in events
    ]

    actions = {
        "Credential Stuffing": "Force password reset, enable MFA, block source IP.",
        "Account Takeover": "Revoke active sessions, verify identity, audit privileged actions.",
        "Potential Insider Threat": "Escalate to HR/Security, review user activity logs.",
        "Impossible Travel": "Verify travel legitimacy, check for VPN/proxy usage.",
    }

    return {
        "alert": alert,
        "alert_type": alert["alert_type"],
        "severity": alert["severity"],
        "user_id": alert["user_id"],
        "timeline": timeline,
        "events": events,
        "confidence": alert["confidence"],
        "recommended_action": actions.get(
            alert["alert_type"],
            "Review correlated events and escalate per SOC playbook.",
        ),
    }
