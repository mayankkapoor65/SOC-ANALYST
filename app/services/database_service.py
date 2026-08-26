from app.database.database import get_connection


def insert_log(
    user_id,
    event_type,
    location,
    device,
    login_hour,
    risk_score,
    status
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO security_logs
        (
            user_id,
            event_type,
            location,
            device,
            login_hour,
            risk_score,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        user_id,
        event_type,
        location,
        device,
        login_hour,
        risk_score,
        status
    ))

    conn.commit()
    conn.close()


def insert_alert(
    user_id,
    severity,
    message
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts
        (
            user_id,
            severity,
            message
        )
        VALUES (?, ?, ?)
    """,
    (
        user_id,
        severity,
        message
    ))

    conn.commit()
    conn.close()


def insert_or_update_twin(
    user_id,
    location,
    device,
    login_hour
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id
        FROM digital_twins
        WHERE user_id = ?
    """, (user_id,))

    existing_user = cursor.fetchone()

    if existing_user:

        cursor.execute("""
            UPDATE digital_twins
            SET
                normal_location = ?,
                normal_device = ?,
                normal_login_hour = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """,
        (
            location,
            device,
            login_hour,
            user_id
        ))

    else:

        cursor.execute("""
            INSERT INTO digital_twins
            (
                user_id,
                normal_location,
                normal_device,
                normal_login_hour
            )
            VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            location,
            device,
            login_hour
        ))

    conn.commit()
    conn.close()


def get_all_logs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM security_logs
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_logs_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM security_logs
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_all_alerts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_all_twins():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM digital_twins
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]