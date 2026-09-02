from types import SimpleNamespace

from django.test import TestCase

from common.api.permissions import IsAdminRole


class IsAdminRoleTests(TestCase):
    def setUp(self):
        self.permission = IsAdminRole()

    def _request_with_user(self, is_authenticated, role=None):
        user = SimpleNamespace(is_authenticated=is_authenticated, role=role)
        return SimpleNamespace(user=user)

    def test_admin_role_is_allowed(self):
        request = self._request_with_user(is_authenticated=True, role="admin")

        self.assertTrue(self.permission.has_permission(request, None))

    def test_client_role_is_denied(self):
        request = self._request_with_user(is_authenticated=True, role="client")

        self.assertFalse(self.permission.has_permission(request, None))

    def test_unauthenticated_user_is_denied(self):
        request = self._request_with_user(is_authenticated=False, role="admin")

        self.assertFalse(self.permission.has_permission(request, None))
