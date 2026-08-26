def calculate_advanced_risk(rule_score, ml_score, deviation_score, hybrid_anomaly=False):
    """
    Combine rule-based score with ML and baseline deviation contributions.

    Formula: final = rule_score + (ml_score * 20) + deviation_score, capped at 100.

    Severity examples (after floor applied when hybrid_anomaly=True):
      rule=20,  ml=0.0,  dev=0  -> 20  LOW      (normal activity)
      rule=60,  ml=0.3,  dev=10 -> 76  MEDIUM   (medium anomaly)
      rule=80,  ml=0.7,  dev=20 -> 100 CRITICAL (high anomaly, capped)
      rule=100, ml=0.95, dev=30 -> 100 CRITICAL (extreme anomaly, capped)
      rule=20,  ml=0.92, dev=10 -> 58  MEDIUM   (ML+baseline lift from LOW)

    When any hybrid layer fires, minimum final risk is 50 (MEDIUM floor).
    """
    ml_contribution = round((ml_score or 0) * 20)
    final_risk = rule_score + ml_contribution + (deviation_score or 0)
    final_risk = min(final_risk, 100)

    if hybrid_anomaly and final_risk < 50:
        final_risk = 50

    return final_risk, classify_risk_level(final_risk)


def classify_risk_level(score):
    """Classify into LOW, MEDIUM, HIGH, CRITICAL."""
    if score >= 90:
        return "CRITICAL"
    if score >= 80:
        return "HIGH"
    if score >= 50:
        return "MEDIUM"
    return "LOW"
