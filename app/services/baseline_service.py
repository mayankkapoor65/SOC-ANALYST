import logging
from datetime import datetime
from collections import Counter

from app.core.time_utils import utc_hours_ago_str, utc_days_ago_str
from app.database.database import get_connection

logger = logging.getLogger(__name__)


def _parse_hour(timestamp):
    if not timestamp:
        return None
    try:
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").hour
    except ValueError:
        return None


def update_user_baseline(user_id, login_hour, location, device, conn=None, exclude_log_id=None):
    """
    Update or create behavioral baseline for a user.
    Called AFTER deviation check so the baseline reflects prior behavior only.
    """
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    cursor = conn.cursor()

    cursor.execute("""
        SELECT normal_login_hour, typical_ip, typical_device, typical_event_frequency
        FROM user_baselines WHERE user_id = ?
    """, (user_id,))
    existing = cursor.fetchone()

    if exclude_log_id is not None:
        cursor.execute("""
            SELECT timestamp, location, device FROM security_logs
            WHERE user_id = ? AND id != ? ORDER BY id DESC LIMIT 50
        """, (user_id, exclude_log_id))
    else:
        cursor.execute("""
            SELECT timestamp, location, device FROM security_logs
            WHERE user_id = ? ORDER BY id DESC LIMIT 50
        """, (user_id,))
    history = cursor.fetchall()

    hours = [_parse_hour(r[0]) for r in history if _parse_hour(r[0]) is not None]
    if not hours:
        hours = [login_hour]
    normal_hour = int(round(sum(hours) / len(hours)))

    locations = [r[1] for r in history if r[1]]
    if not locations:
        locations = [location]
    typical_ip = Counter(locations).most_common(1)[0][0]

    devices = [r[2] for r in history if r[2]]
    if not devices:
        devices = [device]
    typical_device = Counter(devices).most_common(1)[0][0]

    day_ago = utc_days_ago_str(1)
    if exclude_log_id is not None:
        cursor.execute("""
            SELECT COUNT(*) FROM security_logs
            WHERE user_id = ? AND timestamp >= ? AND id != ?
        """, (user_id, day_ago, exclude_log_id))
    else:
        cursor.execute("""
            SELECT COUNT(*) FROM security_logs
            WHERE user_id = ? AND timestamp >= ?
        """, (user_id, day_ago))
    typical_frequency = cursor.fetchone()[0]

    if existing:
        cursor.execute("""
            UPDATE user_baselines SET
                normal_login_hour = ?,
                typical_ip = ?,
                typical_device = ?,
                typical_event_frequency = ?,
                updated_at = datetime('now')
            WHERE user_id = ?
        """, (normal_hour, typical_ip, typical_device, typical_frequency, user_id))
    else:
        cursor.execute("""
            INSERT INTO user_baselines
            (user_id, normal_login_hour, typical_ip, typical_device, typical_event_frequency)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, normal_hour, typical_ip, typical_device, typical_frequency))

    conn.commit()
    if close_conn:
        conn.close()


def check_baseline_deviation(user_id, login_hour, location, device, conn=None, exclude_log_id=None):
    """
    Compare current event against stored user baseline.
    Must run BEFORE update_user_baseline() so deviations are detected
    against the previous profile, not the event being ingested.
    """
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    cursor = conn.cursor()
    cursor.execute("""
        SELECT normal_login_hour, typical_ip, typical_device, typical_event_frequency
        FROM user_baselines WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()

    if not row:
        if close_conn:
            conn.close()
        return {
            "baseline_deviation": False,
            "reason": None,
            "deviation_score": 0,
        }

    normal_hour, typical_ip, typical_device, typical_freq = row
    reasons = []
    deviation_score = 0

    if abs(login_hour - normal_hour) >= 4:
        reasons.append("Login hour differs from normal behavior")
        deviation_score += 10

    if location != typical_ip:
        reasons.append("New location detected")
        deviation_score += 10

    if device != typical_device:
        reasons.append("New device detected")
        deviation_score += 10

    one_hour_ago = utc_hours_ago_str(1)
    if exclude_log_id is not None:
        cursor.execute("""
            SELECT COUNT(*) FROM security_logs
            WHERE user_id = ? AND timestamp >= ? AND id != ?
        """, (user_id, one_hour_ago, exclude_log_id))
    else:
        cursor.execute("""
            SELECT COUNT(*) FROM security_logs
            WHERE user_id = ? AND timestamp >= ?
        """, (user_id, one_hour_ago))
    current_freq = cursor.fetchone()[0]

    if typical_freq > 0 and current_freq > typical_freq * 2:
        reasons.append("Event frequency exceeds normal pattern")
        deviation_score += 10

    if close_conn:
        conn.close()

    return {
        "baseline_deviation": len(reasons) > 0,
        "reason": "; ".join(reasons) if reasons else None,
        "deviation_score": min(deviation_score, 30),
    }


def get_all_baselines():
    """Return all user behavioral baselines."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, normal_login_hour, typical_ip, typical_device,
               typical_event_frequency, updated_at
        FROM user_baselines
        ORDER BY user_id ASC
    """)

    baselines = [
        {
            "user": row[0],
            "normal_login_hour": row[1],
            "typical_ip": row[2],
            "typical_device": row[3],
            "typical_event_frequency": row[4],
            "updated_at": row[5],
        }
        for row in cursor.fetchall()
    ]

    conn.close()
    return {"baselines": baselines, "total_users": len(baselines)}
