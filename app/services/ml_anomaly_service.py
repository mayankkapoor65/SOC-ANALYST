import os
import logging
from datetime import datetime

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.core.time_utils import utc_hours_ago_str
from app.database.database import get_connection

logger = logging.getLogger(__name__)

_MODELS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "models",
)
MODEL_PATH = os.path.join(_MODELS_DIR, "isolation_forest.pkl")
SCALER_PATH = os.path.join(_MODELS_DIR, "scaler.pkl")

ALLOWED_MODEL_FILENAMES = {"isolation_forest.pkl", "scaler.pkl"}

ALLOWED_MODEL_FILES = {
    os.path.realpath(MODEL_PATH),
    os.path.realpath(SCALER_PATH),
}

MIN_TRAINING_SAMPLES = 10
FEATURE_NAMES = ["login_hour", "elevated_risk_count", "event_frequency", "risk_score"]
_model_cache = None
_scaler_cache = None


def _ensure_model_dir():
    os.makedirs(_MODELS_DIR, exist_ok=True)


def _safe_realpath(path):
    """Resolve path and ensure it stays inside the models directory."""
    resolved = os.path.realpath(path)
    models_root = os.path.realpath(_MODELS_DIR)
    if not resolved.startswith(models_root + os.sep) and resolved != models_root:
        raise ValueError(f"Model path outside allowed directory: {path}")
    return resolved


def _safe_joblib_load(path):
    """
    Load a joblib artifact only from the trusted models/ directory.
    Returns None on any failure so POST /log never crashes due to ML.
    """
    try:
        filename = os.path.basename(path)
        if filename not in ALLOWED_MODEL_FILENAMES:
            logger.error("Rejected load of unexpected model filename: %s", filename)
            return None
        safe_path = _safe_realpath(path)
        if safe_path not in ALLOWED_MODEL_FILES:
            logger.error("Rejected load from untrusted path: %s", path)
            return None
        if not os.path.isfile(safe_path):
            logger.warning("Model artifact not found: %s", safe_path)
            return None
        logger.info("Loading model artifact: %s", filename)
        return joblib.load(safe_path)
    except Exception as exc:
        logger.error("Failed to load model artifact %s: %s", path, exc)
        return None


def _clear_caches():
    global _model_cache, _scaler_cache
    _model_cache = None
    _scaler_cache = None


def _unavailable_ml_result(message="ML detection unavailable"):
    return {
        "ml_anomaly": False,
        "anomaly_score": 0.0,
        "ml_score": 0.0,
        "model": "IsolationForest",
        "model_ready": False,
        "message": message,
    }


def _build_feature_matrix(rows):
    """
    Batch-build training features without O(n²) DB queries.
    Excludes the current row from per-user frequency counts (no leakage).
    """
    if not rows:
        return np.empty((0, 4))

    one_hour_ago = utc_hours_ago_str(1)
    user_elevated = {}
    user_recent = {}

    parsed = []
    for row in rows:
        log_id, user_id, risk_score, timestamp, stored_hour = row
        if stored_hour is not None:
            login_hour = stored_hour
        elif timestamp:
            try:
                login_hour = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").hour
            except ValueError:
                login_hour = 12
        else:
            login_hour = 12

        elevated = 1 if (risk_score or 0) >= 50 else 0
        recent = 1 if timestamp and timestamp >= one_hour_ago else 0
        user_elevated[user_id] = user_elevated.get(user_id, 0) + elevated
        user_recent[user_id] = user_recent.get(user_id, 0) + recent
        parsed.append((log_id, user_id, risk_score or 0, login_hour, elevated, recent))

    features = []
    for log_id, user_id, risk_score, login_hour, elevated, recent in parsed:
        elevated_count = user_elevated.get(user_id, 0) - elevated
        recent_count = user_recent.get(user_id, 0) - recent
        features.append([
            login_hour,
            max(elevated_count, 0),
            max(recent_count, 0),
            risk_score,
        ])

    return np.array(features)


def extract_features(user_id, risk_score, login_hour, conn=None, exclude_log_id=None):
    """Build feature vector: login_hour, elevated_risk_count, event_frequency, risk_score."""
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    cursor = conn.cursor()
    one_hour_ago = utc_hours_ago_str(1)

    if exclude_log_id is not None:
        cursor.execute("""
            SELECT COUNT(*) FROM security_logs
            WHERE user_id = ? AND risk_score >= 50 AND id != ?
        """, (user_id, exclude_log_id))
    else:
        cursor.execute("""
            SELECT COUNT(*) FROM security_logs
            WHERE user_id = ? AND risk_score >= 50
        """, (user_id,))

    elevated_risk_count = cursor.fetchone()[0]

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

    event_frequency = cursor.fetchone()[0]

    if close_conn:
        conn.close()

    vector = np.array([[login_hour, elevated_risk_count, event_frequency, risk_score]])
    return {
        "login_hour": login_hour,
        "elevated_risk_count": elevated_risk_count,
        "event_frequency": event_frequency,
        "risk_score": risk_score,
        "vector": vector,
    }


def load_training_data(conn=None):
    """Load historical logs and build normalized-ready feature matrix."""
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, risk_score, timestamp, login_hour
        FROM security_logs
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()

    if close_conn:
        conn.close()

    return _build_feature_matrix(rows)


def train_isolation_forest(data=None):
    """Train StandardScaler + Isolation Forest on historical data."""
    _ensure_model_dir()

    if data is None:
        data = load_training_data()

    if len(data) < MIN_TRAINING_SAMPLES:
        logger.warning(
            "Insufficient training data (%s rows). Need at least %s.",
            len(data), MIN_TRAINING_SAMPLES,
        )
        return None

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)

    contamination = min(0.2, max(0.05, 5 / len(data)))
    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,
    )
    model.fit(scaled_data)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    _clear_caches()
    logger.info("Isolation Forest + StandardScaler trained on %s samples", len(data))
    return model


def load_scaler():
    """Load cached scaler or from disk; returns None on failure."""
    global _scaler_cache

    if _scaler_cache is not None:
        return _scaler_cache

    artifact = _safe_joblib_load(SCALER_PATH)
    if artifact is not None:
        _scaler_cache = artifact
    return _scaler_cache


def load_model():
    """Load cached model or train from existing data; never raises."""
    global _model_cache

    if _model_cache is not None:
        return _model_cache

    artifact = _safe_joblib_load(MODEL_PATH)
    if artifact is not None:
        _model_cache = artifact
        load_scaler()
        return _model_cache

    try:
        data = load_training_data()
        if len(data) >= MIN_TRAINING_SAMPLES:
            _model_cache = train_isolation_forest(data)
            return _model_cache
    except Exception as exc:
        logger.error("Auto-training failed: %s", exc)

    return None


def detect_ml_anomaly(user_id, risk_score, login_hour, conn=None, exclude_log_id=None):
    """
    Run Isolation Forest anomaly detection on scaled features.
    Never raises — returns model_ready=false on any failure.
    """
    try:
        features = extract_features(
            user_id, risk_score, login_hour, conn=conn, exclude_log_id=exclude_log_id
        )
        model = load_model()
        scaler = load_scaler()

        if model is None or scaler is None:
            return _unavailable_ml_result()

        scaled = scaler.transform(features["vector"])
        prediction = model.predict(scaled)[0]
        raw_score = model.decision_function(scaled)[0]

        anomaly_score = round(float(max(0.0, min(1.0, 0.5 - raw_score))), 2)
        ml_anomaly = prediction == -1

        return {
            "ml_anomaly": bool(ml_anomaly),
            "anomaly_score": anomaly_score if ml_anomaly else round(max(0.0, anomaly_score * 0.3), 2),
            "ml_score": anomaly_score if ml_anomaly else round(max(0.0, anomaly_score * 0.3), 2),
            "model": "IsolationForest",
            "model_ready": True,
        }
    except Exception as exc:
        logger.error("ML detection failed for user=%s: %s", user_id, exc)
        return _unavailable_ml_result(str(exc))


def get_ml_anomaly_stats():
    """Return ML anomaly statistics from the anomalies table."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE ml_anomaly = 1")
    total_ml = cursor.fetchone()[0]

    cursor.execute("""
        SELECT AVG(confidence_score) FROM anomalies
        WHERE ml_anomaly = 1 AND confidence_score IS NOT NULL
    """)
    avg_confidence = cursor.fetchone()[0] or 0.0

    cursor.execute("""
        SELECT user_id, anomaly_score, ml_score, confidence_score, created_at, anomaly_type
        FROM anomalies
        WHERE ml_anomaly = 1
        ORDER BY id DESC
        LIMIT 10
    """)
    latest = [
        {
            "user_id": row[0],
            "anomaly_score": row[1],
            "ml_score": row[2],
            "confidence": row[3],
            "created_at": row[4],
            "anomaly_type": row[5],
        }
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "total_ml_anomalies": total_ml,
        "average_confidence": round(avg_confidence, 2),
        "model": "IsolationForest",
        "latest_ml_anomalies": latest,
    }
