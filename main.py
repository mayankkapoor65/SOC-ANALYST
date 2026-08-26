import logging

from app.core.time_utils import utc_now_str, utc_now_hour
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from pydantic import BaseModel, Field

from app.auth.dependencies import require_permission
from app.auth.router import router as auth_router
from app.auth.rbac import (
    PERM_ALERTS,
    PERM_ANALYTICS,
    PERM_ANOMALIES,
    PERM_BASELINES,
    PERM_CORRELATION,
    PERM_DASHBOARD,
    PERM_INCIDENT,
    PERM_INVESTIGATION,
    PERM_ML_EXPLAIN,
    PERM_THREAT_INTEL,
)
from app.core.settings import settings
from app.core.security_checks import validate_security_config, warn_if_default_admin_active
from app.database.database import get_connection, initialize_database, seed_default_admin, seed_demo_users
from app.services.realtime_dashboard_service import get_realtime_dashboard
from app.services.analytics_service import get_analytics_data
from app.services.anomaly_service import get_anomaly_stats
from app.services.hybrid_detection_service import run_hybrid_detection
from app.services.advanced_risk_service import calculate_advanced_risk
from app.services.baseline_service import update_user_baseline, get_all_baselines
from app.services.ml_anomaly_service import get_ml_anomaly_stats
from app.services.mitre_mapping_service import map_to_mitre
from app.services.investigation_service import get_investigation, get_all_alerts
from app.services.incident_report_service import generate_incident_report
from app.services.threat_intelligence_service import get_threat_intel_summary, lookup_ip, enrich_ioc
from app.services.correlation_engine import run_correlation_engine, get_correlation_alerts, get_correlation_alert_detail
from app.services.explainable_ml_service import explain_log

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_database()
validate_security_config()
seed_default_admin()
seed_demo_users()
warn_if_default_admin_active()

app.include_router(auth_router)


class SecurityLog(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    event_type: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=200)
    device: str = Field(..., min_length=1, max_length=200)
    source_ip: Optional[str] = Field(default=None, max_length=45)


@app.get("/")
def root():
    return {
        "message": "Security Log Anomaly Detection System Running",
        "version": settings.API_VERSION,
        "auth_required": settings.AUTH_REQUIRED,
    }


@app.get("/health")
def health_check():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        logger.error("Health check failed: %s", exc)
        raise HTTPException(status_code=503, detail="Database unavailable")


@app.get("/realtime-dashboard")
def realtime_dashboard(_user: dict = Depends(require_permission(PERM_DASHBOARD))):
    try:
        return get_realtime_dashboard()
    except Exception as exc:
        logger.error("Realtime dashboard error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load dashboard data")


@app.get("/analytics")
def analytics(_user: dict = Depends(require_permission(PERM_ANALYTICS))):
    try:
        return get_analytics_data()
    except Exception as exc:
        logger.error("Analytics error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load analytics data")


@app.get("/anomalies")
def anomalies(_user: dict = Depends(require_permission(PERM_ANOMALIES))):
    try:
        return get_anomaly_stats()
    except Exception as exc:
        logger.error("Anomalies error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load anomaly data")


@app.get("/ml-anomalies")
def ml_anomalies(_user: dict = Depends(require_permission(PERM_ANOMALIES))):
    try:
        return get_ml_anomaly_stats()
    except Exception as exc:
        logger.error("ML anomalies error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load ML anomaly data")


@app.get("/user-baselines")
def user_baselines(_user: dict = Depends(require_permission(PERM_BASELINES))):
    try:
        return get_all_baselines()
    except Exception as exc:
        logger.error("User baselines error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load user baselines")


@app.get("/alerts")
def alerts(_user: dict = Depends(require_permission(PERM_ALERTS))):
    try:
        return get_all_alerts()
    except Exception as exc:
        logger.error("Alerts error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load alerts")


@app.get("/investigation/{alert_id}")
def investigation(alert_id: int, _user: dict = Depends(require_permission(PERM_INVESTIGATION))):
    if alert_id < 1:
        raise HTTPException(status_code=400, detail="Invalid alert ID")
    try:
        result = get_investigation(alert_id)
        if not result:
            raise HTTPException(status_code=404, detail="Alert not found")
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Investigation error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load investigation")


@app.get("/incident-report/{alert_id}")
def incident_report(alert_id: int, _user: dict = Depends(require_permission(PERM_INCIDENT))):
    if alert_id < 1:
        raise HTTPException(status_code=400, detail="Invalid alert ID")
    try:
        report = generate_incident_report(alert_id)
        if not report:
            raise HTTPException(status_code=404, detail="Alert not found")
        return report
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Incident report error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to generate incident report")


@app.get("/threat-intel")
def threat_intel(_user: dict = Depends(require_permission(PERM_THREAT_INTEL))):
    try:
        return get_threat_intel_summary()
    except Exception as exc:
        logger.error("Threat intel error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load threat intelligence")


@app.get("/threat-intel/ip/{ip}")
def threat_intel_ip(ip: str, _user: dict = Depends(require_permission(PERM_THREAT_INTEL))):
    try:
        result = lookup_ip(ip)
        if not result:
            return {
                "ip": ip,
                "threat_score": 0,
                "category": "Unknown",
                "confidence": 0.0,
                "severity": "LOW",
                "context": "No threat intelligence match found.",
            }
        return result
    except Exception as exc:
        logger.error("Threat intel lookup error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to lookup IP")


@app.get("/correlation-alerts")
def correlation_alerts(_user: dict = Depends(require_permission(PERM_CORRELATION))):
    try:
        return get_correlation_alerts()
    except Exception as exc:
        logger.error("Correlation alerts error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load correlation alerts")


@app.get("/correlation-alerts/{alert_id}")
def correlation_alert_detail(alert_id: int, _user: dict = Depends(require_permission(PERM_CORRELATION))):
    if alert_id < 1:
        raise HTTPException(status_code=400, detail="Invalid alert ID")
    try:
        result = get_correlation_alert_detail(alert_id)
        if not result:
            raise HTTPException(status_code=404, detail="Correlation alert not found")
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Correlation alert detail error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load correlation alert")


@app.get("/ml-explanation/{log_id}")
def ml_explanation(log_id: int, _user: dict = Depends(require_permission(PERM_ML_EXPLAIN))):
    if log_id < 1:
        raise HTTPException(status_code=400, detail="Invalid log ID")
    try:
        result = explain_log(log_id)
        if not result:
            raise HTTPException(status_code=404, detail="Log not found")
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("ML explanation error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to generate ML explanation")


@app.post("/log")
def create_log(log: SecurityLog):
    rule_risk_score = 20

    if log.location in ["Russia", "China"]:
        rule_risk_score += 40

    if log.device == "Unknown Device":
        rule_risk_score += 40

    login_hour = utc_now_hour()
    timestamp = utc_now_str()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO security_logs
            (
                user_id,
                event_type,
                location,
                device,
                risk_score,
                anomaly_status,
                timestamp,
                login_hour,
                rule_risk_score,
                source_ip
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log.user_id,
            log.event_type,
            log.location,
            log.device,
            rule_risk_score,
            "ANOMALY" if rule_risk_score >= 50 else "NORMAL",
            timestamp,
            login_hour,
            rule_risk_score,
            log.source_ip,
        ))
        conn.commit()
        log_id = cursor.lastrowid

        hybrid_result = run_hybrid_detection(
            user_id=log.user_id,
            risk_score=rule_risk_score,
            login_hour=login_hour,
            location=log.location,
            device=log.device,
            conn=conn,
            log_id=log_id,
        )

        update_user_baseline(
            log.user_id, login_hour, log.location, log.device,
            conn=conn, exclude_log_id=log_id,
        )

        hybrid_risk_score, risk_level = calculate_advanced_risk(
            rule_risk_score,
            hybrid_result.get("ml_score", 0),
            hybrid_result.get("deviation_score", 0),
            hybrid_anomaly=hybrid_result["anomaly"],
        )

        cursor.execute("""
            UPDATE security_logs SET
                rule_risk_score = ?,
                hybrid_risk_score = ?,
                risk_score = ?,
                anomaly_status = ?,
                ml_anomaly = ?,
                ml_score = ?,
                baseline_deviation = ?,
                confidence_score = ?
            WHERE id = ?
        """, (
            rule_risk_score,
            hybrid_risk_score,
            hybrid_risk_score,
            "ANOMALY" if hybrid_result["anomaly"] else "NORMAL",
            int(hybrid_result["ml_anomaly"]),
            hybrid_result.get("ml_score", 0),
            int(hybrid_result["baseline_deviation"]),
            hybrid_result["confidence"],
            log_id,
        ))
        conn.commit()

        if hybrid_risk_score >= 80:
            mitre = map_to_mitre(
                anomaly_type=hybrid_result.get("anomaly_type"),
                event_type=log.event_type,
                description=f"Suspicious activity detected. Risk Score = {hybrid_risk_score}",
                risk_score=hybrid_risk_score,
                baseline_deviation=hybrid_result.get("baseline_deviation", False),
                ml_anomaly=hybrid_result.get("ml_anomaly", False),
            )
            cursor.execute("""
                INSERT INTO alerts
                (user_id, severity, description, timestamp, source_ip,
                 mitre_technique_id, mitre_technique_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                log.user_id,
                "HIGH" if hybrid_risk_score < 90 else "CRITICAL",
                f"Suspicious activity detected. Risk Score = {hybrid_risk_score}",
                timestamp,
                log.location,
                mitre["technique_id"],
                mitre["technique_name"],
            ))
            conn.commit()

        run_correlation_engine(log.user_id, conn=conn)

        conn.close()
    except Exception as exc:
        logger.error("Log ingestion failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to ingest log")

    logger.info(
        "Log ingested user=%s rule_risk=%s hybrid_risk=%s level=%s hybrid=%s",
        log.user_id, rule_risk_score, hybrid_risk_score, risk_level, hybrid_result["anomaly"],
    )

    threat_context = enrich_ioc(ip=log.source_ip, location=log.location)

    response = {
        "status": "success",
        "risk_score": rule_risk_score,
        "rule_risk_score": rule_risk_score,
        "hybrid_risk_score": hybrid_risk_score,
        "risk_level": risk_level,
        "anomaly_detected": hybrid_result["anomaly_detected"],
        "anomaly_score": hybrid_result["anomaly_score"],
        "anomaly_type": hybrid_result["anomaly_type"],
        "rule_anomaly": hybrid_result["rule_anomaly"],
        "ml_anomaly": hybrid_result["ml_anomaly"],
        "baseline_deviation": hybrid_result["baseline_deviation"],
        "confidence": hybrid_result["confidence"],
    }

    if threat_context:
        response["threat_intel"] = {
            "ip": threat_context.get("ip", log.source_ip or log.location),
            "threat_score": threat_context["threat_score"],
            "category": threat_context["category"],
            "confidence": threat_context["confidence"],
        }

    if hybrid_result.get("ml_anomaly"):
        try:
            explanation = explain_log(log_id)
            if explanation:
                response["ml_explanation"] = {
                    "anomaly_score": explanation.get("anomaly_score"),
                    "top_factors": explanation.get("top_factors", []),
                    "explanation_summary": explanation.get("explanation_summary"),
                }
        except Exception as exc:
            logger.warning("ML explanation skipped for log_id=%s: %s", log_id, exc)

    return response
