import logging
from typing import Optional

from app.auth.password import hash_password, verify_password
from app.core.time_utils import utc_now_str
from app.database.database import get_connection

logger = logging.getLogger(__name__)


def get_user_by_username(username: str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, password_hash, role, created_at FROM users WHERE username = ?",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "password_hash": row[3],
        "role": row[4],
        "created_at": row[5],
    }


def get_user_by_id(user_id: int) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, role, created_at FROM users WHERE id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "role": row[3],
        "created_at": row[4],
    }


def create_user(username: str, email: str, password: str, role: str = "VIEWER") -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    created_at = utc_now_str()
    cursor.execute(
        """
        INSERT INTO users (username, email, password_hash, role, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (username, email, hash_password(password), role.upper(), created_at),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    logger.info("Created user username=%s role=%s", username, role)
    return {
        "id": user_id,
        "username": username,
        "email": email,
        "role": role.upper(),
        "created_at": created_at,
    }


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"],
    }


def count_users() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count
