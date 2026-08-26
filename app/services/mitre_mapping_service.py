"""
MITRE ATT&CK technique mapping for security events and anomalies.
"""

MITRE_TECHNIQUES = {
    "T1110": {"technique_id": "T1110", "technique_name": "Brute Force"},
    "T1078": {"technique_id": "T1078", "technique_name": "Valid Accounts"},
    "T1087": {"technique_id": "T1087", "technique_name": "Account Discovery"},
    "T1499": {"technique_id": "T1499", "technique_name": "Endpoint Denial of Service"},
    "T1021": {"technique_id": "T1021", "technique_name": "Remote Services"},
    "T1071": {"technique_id": "T1071", "technique_name": "Application Layer Protocol"},
}

# Pattern → MITRE mapping
ANOMALY_TYPE_MAP = {
    "High Risk Spike": "T1499",
    "Behavior Deviation": "T1078",
    "ML Outlier": "T1078",
    "Baseline Deviation": "T1078",
    "Hybrid Detection": "T1078",
}

EVENT_TYPE_MAP = {
    "failed_login": "T1110",
    "failed login": "T1110",
    "login_failure": "T1110",
    "enumeration": "T1087",
    "account_discovery": "T1087",
    "login": "T1078",
    "successful_login": "T1078",
}


def map_to_mitre(
    anomaly_type=None,
    event_type=None,
    description=None,
    risk_score=0,
    baseline_deviation=False,
    ml_anomaly=False,
):
    """
    Map a security event to a MITRE ATT&CK technique.

    Mapping rules:
      Repeated Failed Logins → T1110 Brute Force
      Successful Login After Failures → T1078 Valid Accounts
      Account Enumeration → T1087 Account Discovery
      Unusual Login Behavior → T1078 Valid Accounts
      Risk Spikes → T1499 Endpoint Denial of Service
    """
    desc_lower = (description or "").lower()
    event_lower = (event_type or "").lower()

    if any(k in desc_lower for k in ("failed login", "brute force", "repeated failure")):
        return _technique("T1110")

    if any(k in desc_lower for k in ("enumeration", "account discovery")):
        return _technique("T1087")

    if any(k in desc_lower for k in ("login after failure", "successful login after")):
        return _technique("T1078")

    if event_lower in EVENT_TYPE_MAP:
        tid = EVENT_TYPE_MAP[event_lower]
        if tid == "T1110" or "fail" in event_lower:
            return _technique("T1110")
        if tid == "T1087":
            return _technique("T1087")

    if anomaly_type and anomaly_type in ANOMALY_TYPE_MAP:
        tid = ANOMALY_TYPE_MAP[anomaly_type]
        if tid == "T1499" or (risk_score or 0) >= 90:
            return _technique("T1499")
        return _technique(tid)

    if baseline_deviation or ml_anomaly:
        return _technique("T1078")

    if (risk_score or 0) >= 90:
        return _technique("T1499")

    if (risk_score or 0) >= 50:
        return _technique("T1078")

    return _technique("T1071")


def _technique(technique_id):
    info = MITRE_TECHNIQUES.get(technique_id, MITRE_TECHNIQUES["T1071"])
    return {
        "technique_id": info["technique_id"],
        "technique_name": info["technique_name"],
    }


def get_recommended_action(mitre_mapping, severity, risk_score):
    """Generate SOC analyst recommended action based on MITRE mapping."""
    tid = mitre_mapping.get("technique_id", "")

    actions = {
        "T1110": "Lock affected account, enforce MFA, and review authentication logs for brute-force patterns.",
        "T1078": "Validate user identity, review recent login locations/devices, and consider session revocation.",
        "T1087": "Investigate enumeration source, restrict directory access, and monitor for follow-on attacks.",
        "T1499": "Isolate affected endpoint, throttle request rate, and escalate to incident response.",
        "T1021": "Review remote access policies and verify VPN/RDP session legitimacy.",
        "T1071": "Monitor network traffic and correlate with threat intelligence feeds.",
    }

    base = actions.get(tid, "Review alert details and escalate per SOC playbook.")

    if severity in ("CRITICAL", "HIGH") or (risk_score or 0) >= 90:
        return f"IMMEDIATE: {base}"
    if (risk_score or 0) >= 50:
        return f"PRIORITY: {base}"
    return f"STANDARD: {base}"
