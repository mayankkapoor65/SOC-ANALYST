import unittest

from app.database.database import initialize_database, get_connection
from app.services.threat_intelligence_service import (
    lookup_ip,
    get_threat_intel_summary,
    classify_threat_severity,
    enrich_ioc,
    _normalize_ioc,
    load_threat_feed,
)
from app.services.correlation_engine import get_correlation_alerts, check_account_takeover


class TestThreatIntelligence(unittest.TestCase):
    def test_lookup_known_ip(self):
        result = lookup_ip("185.200.10.15")
        self.assertIsNotNone(result)
        self.assertEqual(result["category"], "Botnet")
        self.assertGreaterEqual(result["threat_score"], 90)

    def test_lookup_unknown_ip(self):
        result = lookup_ip("1.2.3.999")
        self.assertIsNone(result)

    def test_summary_has_counts(self):
        summary = get_threat_intel_summary()
        self.assertIn("total_iocs", summary)
        self.assertIn("malicious_ips", summary)
        self.assertGreater(summary["total_iocs"], 0)

    def test_location_enrichment(self):
        result = enrich_ioc(location="Russia")
        self.assertIsNotNone(result)
        self.assertGreater(result["threat_score"], 0)

    def test_severity_classification(self):
        self.assertEqual(classify_threat_severity(95), "CRITICAL")
        self.assertEqual(classify_threat_severity(30), "LOW")

    def test_invalid_threat_score_defaults_to_zero(self):
        ioc = _normalize_ioc({"ip": "1.2.3.4", "threat_score": "bad"})
        self.assertEqual(ioc["threat_score"], 0)
        self.assertEqual(ioc["severity"], "LOW")

    def test_malformed_feed_entry_does_not_crash_load(self):
        import app.services.threat_intelligence_service as ti

        original = dict(ti._ioc_cache)
        ti._ioc_cache = {}
        ti._cache_loaded = False
        try:
            ti._ioc_cache = {
                "1.2.3.4": _normalize_ioc({"ip": "1.2.3.4", "threat_score": "bad"}),
            }
            ti._cache_loaded = True
            summary = get_threat_intel_summary()
            self.assertEqual(summary["total_iocs"], 1)
            self.assertEqual(summary["average_threat_score"], 0)
        finally:
            ti._ioc_cache = original
            ti._cache_loaded = True
            load_threat_feed(force_reload=True)


class TestCorrelationEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()

    def test_get_alerts_returns_structure(self):
        result = get_correlation_alerts()
        self.assertIn("alerts", result)
        self.assertIn("total", result)

    def test_account_takeover_skipped_without_baseline(self):
        conn = get_connection()
        cursor = conn.cursor()
        user_id = "v101_no_baseline_user"
        cursor.execute("DELETE FROM correlation_alerts WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM security_logs WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_baselines WHERE user_id = ?", (user_id,))
        conn.commit()

        events = [
            ("new_device_login", "US", "unknown-phone", 80),
            ("high_risk_login", "US", "unknown-phone", 85),
            ("privileged_access", "US", "unknown-phone", 90),
        ]
        for event_type, location, device, risk in events:
            cursor.execute("""
                INSERT INTO security_logs
                (user_id, event_type, location, device, risk_score, hybrid_risk_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (user_id, event_type, location, device, risk, risk))
        conn.commit()

        alert_id = check_account_takeover(user_id, conn)
        conn.close()
        self.assertIsNone(alert_id)


if __name__ == "__main__":
    unittest.main()
