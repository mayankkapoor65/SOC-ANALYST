from app.database.database import get_connection


def update_behavior_profile(
    user_id,
    location,
    device,
    login_hour
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM digital_twins
        WHERE user_id=?
    """, (user_id,))

    twin = cursor.fetchone()

    if not twin:
        conn.close()
        return

    cursor.execute("""
        UPDATE digital_twins
        SET
            location=?,
            device=?,
            login_hour=?
        WHERE user_id=?
    """, (
        location,
        device,
        login_hour,
        user_id
    ))

    conn.commit()
    conn.close()

    return {
        "adaptive_learning": True,
        "updated_user": user_id
    }