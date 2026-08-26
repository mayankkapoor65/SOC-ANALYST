import os
import unittest
from unittest.mock import patch

os.environ.setdefault("AUTH_REQUIRED", "true")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only")


class TestDemoUserSeeding(unittest.TestCase):
    def test_seed_demo_users_is_idempotent(self):
        from app.database.database import initialize_database, seed_demo_users, DEMO_USERS
        from app.auth.user_service import get_user_by_username, count_users

        initialize_database()
        before = count_users()
        seed_demo_users()
        after_first = count_users()
        seed_demo_users()
        after_second = count_users()

        self.assertEqual(after_first, after_second)
        self.assertGreaterEqual(after_first - before, 0)

        for username, _password, role, _email in DEMO_USERS:
            user = get_user_by_username(username)
            self.assertIsNotNone(user, f"Expected demo user {username}")
            self.assertEqual(user["role"], role)


class TestGuestAccess(unittest.TestCase):
    def test_guest_header_grants_viewer_read_permissions(self):
        from app.auth.guest import GUEST_READ_PERMISSIONS, GUEST_USER, is_guest_request
        from app.auth.rbac import (
            PERM_ANALYTICS,
            PERM_DASHBOARD,
            PERM_INVESTIGATION,
            PERM_ADMIN,
        )

        class FakeRequest:
            headers = {"x-sentinel-guest": "1"}

        self.assertTrue(is_guest_request(FakeRequest()))
        self.assertIn(PERM_DASHBOARD, GUEST_READ_PERMISSIONS)
        self.assertIn(PERM_ANALYTICS, GUEST_READ_PERMISSIONS)
        self.assertNotIn(PERM_INVESTIGATION, GUEST_READ_PERMISSIONS)
        self.assertNotIn(PERM_ADMIN, GUEST_READ_PERMISSIONS)
        self.assertEqual(GUEST_USER["role"], "VIEWER")
        self.assertEqual(GUEST_USER["username"], "guest")

    def test_demo_credentials_authenticate(self):
        from app.database.database import initialize_database, seed_demo_users
        from app.auth.user_service import authenticate_user

        initialize_database()
        seed_demo_users()

        admin = authenticate_user("admin", "Admin123!")
        analyst = authenticate_user("analyst1", "Analyst123!")
        viewer = authenticate_user("viewer1", "Viewer123!")

        self.assertEqual(admin["role"], "ADMIN")
        self.assertEqual(analyst["role"], "ANALYST")
        self.assertEqual(viewer["role"], "VIEWER")


if __name__ == "__main__":
    unittest.main()
