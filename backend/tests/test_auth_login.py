import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from app.auth import service
from app.auth.schema import TokenResponse


class TestAuthLogin(unittest.TestCase):
    def test_login_returns_user_profile_with_access_token(self):
        user = SimpleNamespace(
            id=7,
            username="operator",
            email="operator@example.com",
            is_active=True,
            created_at=datetime(2026, 1, 1),
            email_verified=False,
            hashed_password="test-hash"
        )

        with patch.object(service.crud, "get_user_by_username", return_value=user), \
             patch.object(service.crud, "get_user_by_email", return_value=None), \
             patch.object(service, "verify_password", return_value=True), \
             patch.object(service, "create_access_token", return_value="test-token"):
            response = TokenResponse.model_validate(
                service.login_user("operator", "test-password")
            )

        self.assertEqual(response.access_token, "test-token")
        self.assertEqual(response.user.username, "operator")
        self.assertEqual(response.user.email, "operator@example.com")


if __name__ == "__main__":
    unittest.main()
