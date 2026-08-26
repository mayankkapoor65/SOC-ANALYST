from app.services.investigation_service import get_investigation
from app.services.mitre_mapping_service import map_to_mitre, MITRE_TECHNIQUES


def generate_incident_report(alert_id: int):
    """Generate structured JSON incident report for an alert."""
    investigation = get_investigation(alert_id)
    if not investigation:
        return None

    mitre = investigation["mitre_mapping"]
    severity = investigation["severity"]
    risk_score = investigation["risk_score"]

    risk_level = "LOW"
    if risk_score >= 90:
        risk_level = "CRITICAL"
    elif risk_score >= 80:
        risk_level = "HIGH"
    elif risk_score >= 50:
        risk_level = "MEDIUM"

    executive_summary = (
        f"Security alert #{alert_id} triggered for user '{investigation['user']}' "
        f"with {severity} severity and risk score {risk_score}. "
        f"MITRE ATT&CK technique {mitre['technique_id']} ({mitre['technique_name']}) "
        f"has been mapped. Immediate analyst review is recommended."
    )

    recommendations = [
        investigation["recommended_action"],
        "Document findings in the SOC ticketing system.",
        "Correlate with threat intelligence and user baseline profiles.",
    ]

    if risk_level in ("CRITICAL", "HIGH"):
        recommendations.insert(0, "Escalate to incident response team within SLA window.")
    if investigation.get("evidence"):
        recommendations.append(
            f"Review {len(investigation['evidence'])} evidence artifact(s) attached to this alert."
        )

    return {
        "report_type": "incident_report",
        "report_version": "1.0",
        "alert_id": alert_id,
        "executive_summary": executive_summary,
        "alert_details": {
            "alert_id": alert_id,
            "user": investigation["user"],
            "severity": severity,
            "source_ip": investigation["source_ip"],
            "timestamp": investigation["alert"]["timestamp"],
            "description": investigation["alert"]["description"],
        },
        "evidence": investigation["evidence"],
        "timeline": investigation["timeline"],
        "mitre_techniques": [
            {
                **mitre,
                "tactic": _tactic_for_technique(mitre["technique_id"]),
                "framework": "MITRE ATT&CK",
            }
        ],
        "risk_assessment": {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "confidence": _estimate_confidence(investigation),
        },
        "recommendations": recommendations,
    }


def _tactic_for_technique(technique_id):
    tactics = {
        "T1110": "Credential Access",
        "T1078": "Initial Access / Persistence",
        "T1087": "Discovery",
        "T1499": "Impact",
        "T1021": "Lateral Movement",
        "T1071": "Command and Control",
    }
    return tactics.get(technique_id, "Multiple")


def _estimate_confidence(investigation):
    evidence_count = len(investigation.get("evidence", []))
    if evidence_count >= 5:
        return "HIGH"
    if evidence_count >= 2:
        return "MEDIUM"
    return "LOW"
