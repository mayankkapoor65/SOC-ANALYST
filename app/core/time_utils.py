"""UTC timestamp helpers — all time-window queries use UTC for consistency."""

from datetime import datetime, timedelta


def utc_now_str():
    """Return current UTC time as YYYY-MM-DD HH:MM:SS (matches stored log format)."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def utc_now_hour():
    """Return current UTC hour (0-23)."""
    return datetime.utcnow().hour


def utc_hours_ago_str(hours=1):
    """Return UTC timestamp string for N hours ago."""
    return (datetime.utcnow() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")


def utc_days_ago_str(days=1):
    """Return UTC timestamp string for N days ago."""
    return (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
