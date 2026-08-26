import sqlite3
import logging

from app.core.settings import settings

logger = logging.getLogger(__name__)

DB_NAME = settings.DB_NAME


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def _column_names(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}


def _add_column_if_missing(cursor, table, column, col_type):
    cols = _column_names(cursor, table)
    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        logger.info("Added column %s.%s", table, column)


def _migrate_legacy_schema(cursor):
    """Migrate old schemas (user_name columns) to the current user_id schema."""
    log_cols = _column_names(cursor, "security_logs")
    if log_cols and "user_name" in log_cols and "user_id" not in log_cols:
        cursor.execute("ALTER TABLE security_logs RENAME COLUMN user_name TO user_id")

    alert_cols = _column_names(cursor, "alerts")
    if alert_cols and "user_name" in alert_cols and "user_id" not in alert_cols:
        cursor.execute("ALTER TABLE alerts RENAME COLUMN user_name TO user_id")

    anomaly_cols = _column_names(cursor, "anomalies")
    if anomaly_cols and "user_name" in anomaly_cols and "user_id" not in anomaly_cols:
        cursor.execute("ALTER TABLE anomalies RENAME COLUMN user_name TO user_id")


def _migrate_phase11_schema(cursor):
    """Add Phase 11 ML/hybrid columns without destroying existing data."""
    _add_column_if_missing(cursor, "security_logs", "login_hour", "INTEGER")
    _add_column_if_missing(cursor, "security_logs", "ml_anomaly", "INTEGER DEFAULT 0")
    _add_column_if_missing(cursor, "security_logs", "ml_score", "REAL DEFAULT 0")
    _add_column_if_missing(cursor, "security_logs", "baseline_deviation", "INTEGER DEFAULT 0")
    _add_column_if_missing(cursor, "security_logs", "confidence_score", "REAL DEFAULT 0")
    _add_column_if_missing(cursor, "security_logs", "rule_risk_score", "INTEGER")

    _add_column_if_missing(cursor, "anomalies", "ml_anomaly", "INTEGER DEFAULT 0")
    _add_column_if_missing(cursor, "anomalies", "ml_score", "REAL DEFAULT 0")
    _add_column_if_missing(cursor, "anomalies", "baseline_deviation", "INTEGER DEFAULT 0")
    _add_column_if_missing(cursor, "anomalies", "confidence_score", "REAL DEFAULT 0")


def _migrate_phase12_schema(cursor):
    """Add Phase 12 SOC platform columns."""
    _add_column_if_missing(cursor, "alerts", "source_ip", "TEXT")
    _add_column_if_missing(cursor, "alerts", "mitre_technique_id", "TEXT")
    _add_column_if_missing(cursor, "alerts", "mitre_technique_name", "TEXT")


def _migrate_phase121_schema(cursor):
    """Phase 12.1: explicit hybrid_risk_score column for analytics consistency."""
    _add_column_if_missing(cursor, "security_logs", "hybrid_risk_score", "INTEGER")

    cols = _column_names(cursor, "security_logs")
    if "hybrid_risk_score" in cols and "risk_score" in cols:
        cursor.execute("""
            UPDATE security_logs
            SET hybrid_risk_score = risk_score
            WHERE hybrid_risk_score IS NULL AND risk_score IS NOT NULL
        """)


def _migrate_phase1315_schema(cursor):
    """Phase 13–15: correlation alerts and optional source IP."""
    _add_column_if_missing(cursor, "security_logs", "source_ip", "TEXT")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS correlation_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        user_id TEXT,
        description TEXT,
        confidence REAL DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS security_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        event_type TEXT,
        location TEXT,
        device TEXT,
        risk_score INTEGER,
        anomaly_status TEXT,
        timestamp TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        severity TEXT,
        description TEXT,
        timestamp TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anomalies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        risk_score INTEGER,
        anomaly_score REAL,
        anomaly_type TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_baselines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE,
        normal_login_hour INTEGER,
        typical_ip TEXT,
        typical_device TEXT,
        typical_event_frequency INTEGER DEFAULT 0,
        updated_at TEXT DEFAULT (datetime('now'))
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'VIEWER',
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    _migrate_legacy_schema(cursor)
    _migrate_phase11_schema(cursor)
    _migrate_phase12_schema(cursor)
    _migrate_phase121_schema(cursor)
    _migrate_phase1315_schema(cursor)

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def seed_default_admin():
    """Create default ADMIN user if no users exist (Phase 12 bootstrap)."""
    from app.auth.user_service import count_users, create_user, get_user_by_username
    from app.core.settings import settings

    if count_users() > 0:
        return

    if get_user_by_username(settings.ADMIN_USERNAME):
        return

    create_user(
        settings.ADMIN_USERNAME,
        settings.ADMIN_EMAIL,
        settings.ADMIN_PASSWORD,
        "ADMIN",
    )
    logger.info("Seeded default ADMIN user: %s", settings.ADMIN_USERNAME)


DEMO_USERS = [
    ("admin", "Admin123!", "ADMIN", "admin@sentinelai.local"),
    ("admin1", "Admin123!", "ADMIN", "admin1@sentinelai.local"),
    ("admin2", "Admin123!", "ADMIN", "admin2@sentinelai.local"),
    ("admin3", "Admin123!", "ADMIN", "admin3@sentinelai.local"),
    ("analyst1", "Analyst123!", "ANALYST", "analyst1@sentinelai.local"),
    ("analyst2", "Analyst123!", "ANALYST", "analyst2@sentinelai.local"),
    ("analyst3", "Analyst123!", "ANALYST", "analyst3@sentinelai.local"),
    ("viewer1", "Viewer123!", "VIEWER", "viewer1@sentinelai.local"),
    ("viewer2", "Viewer123!", "VIEWER", "viewer2@sentinelai.local"),
    ("viewer3", "Viewer123!", "VIEWER", "viewer3@sentinelai.local"),
]


def seed_demo_users():
    """Seed demo accounts for presentations (Phase 12.2). Idempotent — skips existing users."""
    from app.auth.user_service import create_user, get_user_by_username

    for username, password, role, email in DEMO_USERS:
        if get_user_by_username(username):
            continue
        try:
            create_user(username, email, password, role)
            logger.info("Seeded demo user username=%s role=%s", username, role)
        except Exception as exc:
            logger.warning("Could not seed demo user %s: %s", username, exc)
