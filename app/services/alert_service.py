def generate_alert(status: str, risk_score: float):

    if status == "ANOMALY":
        return {
            "alert": True,
            "severity": "HIGH",
            "message": f"Suspicious activity detected. Risk Score = {risk_score}"
        }

    return {
        "alert": False,
        "severity": "LOW",
        "message": "No anomaly detected"
    }