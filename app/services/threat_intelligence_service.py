"""
Threat Intelligence Service — IOC enrichment with pluggable feed backends.

Supports: local mock feed, JSON feed, CSV feed.
Designed for future integration with AbuseIPDB, AlienVault OTX, ThreatFox, VirusTotal.
"""

import csv
import json
import logging
import os
from typing import Optional

from app.core.settings import settings

logger = logging.getLogger(__name__)

_MALICIOUS_CATEGORIES = {"Malicious", "Botnet", "Scanner"}
_SUSPICIOUS_CATEGORIES = {"Suspicious"}

_ioc_cache: dict = {}
_cache_loaded = False


def _project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def _default_feed_path():
    return os.path.join(_project_root(), "sample_data", "threat_feed.json")


def _load_json_feed(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return data.get("iocs", data.get("threats", []))


def _safe_threat_score(value, entry_ip: str = "") -> int:
    if value is None or value == "":
        return 0
    try:
        return int(float(value))
    except (TypeError, ValueError):
        logger.warning(
            "Invalid threat_score %r for IOC %s; defaulting to 0",
            value,
            entry_ip or "unknown",
        )
        return 0


def _safe_confidence(value, entry_ip: str = "") -> float:
    if value is None or value == "":
        return 0.5
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        logger.warning(
            "Invalid confidence %r for IOC %s; defaulting to 0.5",
            value,
            entry_ip or "unknown",
        )
        return 0.5


def _load_csv_feed(path: str) -> list:
    records = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ip = row.get("ip", "")
            records.append({
                "ip": ip,
                "threat_score": _safe_threat_score(row.get("threat_score", 0), ip),
                "category": row.get("category", "Unknown"),
                "confidence": _safe_confidence(row.get("confidence", 0.5), ip),
                "location": row.get("location"),
            })
    return records


def _normalize_ioc(entry: dict) -> dict:
    ip = entry.get("ip", "")
    threat_score = _safe_threat_score(entry.get("threat_score", 0), ip)
    return {
        "ip": ip,
        "threat_score": threat_score,
        "category": entry.get("category", "Unknown"),
        "confidence": _safe_confidence(entry.get("confidence", 0.5), ip),
        "location": entry.get("location"),
        "severity": classify_threat_severity(threat_score),
    }


def classify_threat_severity(threat_score: int) -> str:
    if threat_score >= 90:
        return "CRITICAL"
    if threat_score >= 70:
        return "HIGH"
    if threat_score >= 40:
        return "MEDIUM"
    return "LOW"


def load_threat_feed(force_reload: bool = False) -> dict:
    """Load IOC feed from configured source into memory cache."""
    global _ioc_cache, _cache_loaded

    if _cache_loaded and not force_reload:
        return _ioc_cache

    feed_type = settings.THREAT_FEED_TYPE.lower()
    feed_path = settings.THREAT_FEED_PATH or _default_feed_path()

    try:
        if feed_type == "json":
            raw = _load_json_feed(feed_path)
        elif feed_type == "csv":
            raw = _load_csv_feed(feed_path)
        else:
            raw = _load_json_feed(_default_feed_path())

        _ioc_cache = {}
        for entry in raw:
            ioc = _normalize_ioc(entry)
            if ioc["ip"]:
                _ioc_cache[ioc["ip"]] = ioc
            if ioc.get("location"):
                _ioc_cache[ioc["location"]] = ioc

        _cache_loaded = True
        logger.info("Loaded %s IOCs from threat feed (%s)", len(_ioc_cache), feed_type)
    except Exception as exc:
        logger.error("Failed to load threat feed: %s", exc)
        _ioc_cache = _mock_feed()
        _cache_loaded = True

    return _ioc_cache


def _mock_feed() -> dict:
    """Built-in mock feed when external feed unavailable."""
    mock = [
        {"ip": "185.200.10.15", "threat_score": 95, "category": "Botnet", "confidence": 0.91},
        {"ip": "103.21.244.0", "threat_score": 88, "category": "Scanner", "confidence": 0.87},
        {"ip": "192.168.100.55", "threat_score": 45, "category": "Suspicious", "confidence": 0.62},
    ]
    return {_normalize_ioc(m)["ip"]: _normalize_ioc(m) for m in mock}


def lookup_ip(ip: str) -> Optional[dict]:
    """Look up a single IP or location against the threat feed."""
    feed = load_threat_feed()
    key = (ip or "").strip()
    if key in feed:
        result = dict(feed[key])
        result["ip"] = key
        result["context"] = generate_threat_context(result)
        return result
    return None


def enrich_ioc(ip: Optional[str] = None, location: Optional[str] = None) -> Optional[dict]:
    """Enrich an event with threat intelligence from IP or location."""
    if ip:
        result = lookup_ip(ip)
        if result:
            return result
    if location:
        return lookup_ip(location)
    return None


def generate_threat_context(ioc: dict) -> str:
    """Generate human-readable threat context for an IOC."""
    category = ioc.get("category", "Unknown")
    score = ioc.get("threat_score", 0)
    severity = ioc.get("severity", classify_threat_severity(score))
    return (
        f"{severity} threat: {category} activity detected "
        f"(score {score}/100, confidence {ioc.get('confidence', 0):.0%})."
    )


def get_threat_intel_summary() -> dict:
    """Return aggregate threat intelligence statistics."""
    feed = load_threat_feed()
    unique = {}
    for key, ioc in feed.items():
        uid = ioc.get("ip") or key
        if uid not in unique:
            unique[uid] = ioc

    iocs = list(unique.values())
    malicious = sum(1 for i in iocs if i["category"] in _MALICIOUS_CATEGORIES)
    suspicious = sum(1 for i in iocs if i["category"] in _SUSPICIOUS_CATEGORIES)
    high_confidence = sum(1 for i in iocs if i["confidence"] >= 0.8)
    avg_score = round(sum(i["threat_score"] for i in iocs) / len(iocs), 2) if iocs else 0

    categories = {}
    for i in iocs:
        cat = i["category"]
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_iocs": len(iocs),
        "malicious_ips": malicious,
        "suspicious_ips": suspicious,
        "high_confidence_threats": high_confidence,
        "average_threat_score": avg_score,
        "categories": categories,
        "feed_type": settings.THREAT_FEED_TYPE,
    }
