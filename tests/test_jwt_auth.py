import os
import unittest
from datetime import timedelta
from unittest.mock import patch

from jose import jwt

# Ensure dev mode for most tests
os.environ.setdefault("AUTH_REQUIRED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only")


class TestJWTAuth(unittest.TestCase):
    def setUp(self):
        from app.auth.jwt_handler import create_access_token, decode_access_token
        self.create_token = create_access_token
        self.decode_token = decode_access_token

    def test_valid_token_decodes(self):
        token = self.create_token({"sub": "1", "role": "ADMIN"})
        payload = self.decode_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], "1")
        self.assertEqual(payload["role"], "ADMIN")

    def test_invalid_token_rejected(self):
        payload = self.decode_token("not.a.valid.token")
        self.assertIsNone(payload)

    def test_tampered_token_rejected(self):
        token = self.create_token({"sub": "1", "role": "ADMIN"})
        payload = self.decode_token(token + "tampered")
        self.assertIsNone(payload)

    def test_expired_token_rejected(self):
        from app.core.settings import settings
        token = self.create_token(
            {"sub": "1", "role": "ADMIN"},
            expires_delta=timedelta(seconds=-1),
        )
        payload = self.decode_token(token)
        self.assertIsNone(payload)

    def test_missing_sub_rejected_by_dependency(self):
        from app.core.settings import settings
        token = jwt.encode(
            {"role": "ADMIN"},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        payload = self.decode_token(token)
        self.assertIsNotNone(payload)
        self.assertNotIn("sub", payload)


class TestRBACEnforcement(unittest.TestCase):
    def test_viewer_allowed_demo_read_permissions(self):
        from app.auth.rbac import (
            role_has_permission,
            PERM_ANALYTICS,
            PERM_DASHBOARD,
            PERM_THREAT_INTEL,
            PERM_CORRELATION,
            PERM_ML_EXPLAIN,
            PERM_INVESTIGATION,
        )
        self.assertTrue(role_has_permission("VIEWER", PERM_DASHBOARD))
        self.assertTrue(role_has_permission("VIEWER", PERM_ANALYTICS))
        self.assertTrue(role_has_permission("VIEWER", PERM_THREAT_INTEL))
        self.assertTrue(role_has_permission("VIEWER", PERM_CORRELATION))
        self.assertTrue(role_has_permission("VIEWER", PERM_ML_EXPLAIN))
        self.assertFalse(role_has_permission("VIEWER", PERM_INVESTIGATION))

    def test_analyst_allowed_analytics(self):
        from app.auth.rbac import role_has_permission, PERM_ANALYTICS, PERM_INVESTIGATION
        self.assertTrue(role_has_permission("ANALYST", PERM_ANALYTICS))
        self.assertTrue(role_has_permission("ANALYST", PERM_INVESTIGATION))

    def test_admin_has_all_permissions(self):
        from app.auth.rbac import role_has_permission, PERM_BASELINES, PERM_ADMIN
        self.assertTrue(role_has_permission("ADMIN", PERM_BASELINES))
        self.assertTrue(role_has_permission("ADMIN", PERM_ADMIN))


class TestSecurityConfig(unittest.TestCase):
    def test_insecure_password_blocked_when_auth_required(self):
        from app.core.security_checks import validate_security_config
        with patch("app.core.security_checks.settings") as mock_settings:
            mock_settings.AUTH_REQUIRED = True
            mock_settings.JWT_SECRET_KEY = "strong-random-secret-value"
            mock_settings.ADMIN_PASSWORD = "Admin123!"
            mock_settings.ADMIN_USERNAME = "admin"
            with self.assertRaises(RuntimeError):
                validate_security_config()

    def test_insecure_jwt_blocked_when_auth_required(self):
        from app.core.security_checks import validate_security_config
        with patch("app.core.security_checks.settings") as mock_settings:
            mock_settings.AUTH_REQUIRED = True
            mock_settings.JWT_SECRET_KEY = "change-me-in-production"
            mock_settings.ADMIN_PASSWORD = "StrongP@ssw0rd!"
            mock_settings.ADMIN_USERNAME = "admin"
            with self.assertRaises(RuntimeError):
                validate_security_config()


if __name__ == "__main__":
    unittest.main()
