from app.schemas.log_schema import SecurityLogCreate
from app.services.anomaly_detection_service import detect_anomaly


def ingest_log(log: SecurityLogCreate):

    result = detect_anomaly(
        log.login_hour,
        log.location
    )

    return {
        "user_id": log.user_id,
        "event_type": log.event_type,
        "risk_score": result["risk_score"],
        "status": result["status"]
    }