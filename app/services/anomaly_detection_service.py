from app.services.risk_scoring_service import calculate_risk_score


def detect_anomaly(login_hour: int, location: str):

    risk_score = calculate_risk_score(
        login_hour,
        location
    )

    if risk_score >= 50:
        status = "ANOMALY"
    else:
        status = "NORMAL"

    return {
        "risk_score": risk_score,
        "status": status
    }