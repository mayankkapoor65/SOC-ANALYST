"""
Legacy database setup script — aligned with the active application schema.
Prefer using initialize_database() from app.database.database at app startup.
"""
import sqlite3

from app.core.settings import settings

conn = sqlite3.connect(settings.DB_NAME)
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

conn.commit()
conn.close()

print("Database tables created successfully.")
