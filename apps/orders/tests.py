from unittest.mock import patch

from rest_framework.test import APITestCase

from apps.catalog.models import ProductModel
from apps.users.models import UserModel


class OrdersApiTests(APITestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testuser", password="123456"
        )
        self.other = UserModel.objects.create_user(username="other", password="123456")
        self.admin = UserModel.objects.create_user(
            username="boss", password="123456", role="admin"
        )
        self.product = ProductModel.objects.create(
            name="Mouse USB", price=15.50, stock=5
        )
        self.client.force_authenticate(self.user)

    def _order(self, **payload):
        payload.setdefault("product_id", self.product.id)
        return self.client.post("/create_order", payload, format="json")

    def test_create_order_success_uses_authenticated_user(self):
        response = self._order(quantity=2)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["total"], 31.0)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        orders = self.client.get("/get_all_orders_legacy").json()
        self.assertEqual(orders[0]["user_id"], self.user.id)

    def test_create_order_ignores_user_id_in_body(self):
        self._order(quantity=1, user_id=self.other.id)

        orders = self.client.get("/get_all_orders_legacy").json()
        self.assertEqual(orders[0]["user_id"], self.user.id)

    def test_create_order_requires_authentication(self):
        self.client.force_authenticate(None)

        self.assertEqual(self._order(quantity=1).status_code, 401)

    def test_create_order_insufficient_stock_returns_400(self):
        self.assertEqual(self._order(quantity=100).status_code, 400)

    def test_create_order_product_not_found_returns_404(self):
        self.assertEqual(self._order(product_id=9999).status_code, 404)

    def test_create_order_invalid_quantity_returns_400(self):
        for quantity in (0, -3, "abc"):
            with self.subTest(quantity=quantity):
                self.assertEqual(self._order(quantity=quantity).status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_create_order_missing_product_returns_400(self):
        response = self.client.post("/create_order", {"quantity": 1}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_list_orders_requires_authentication(self):
        self.client.force_authenticate(None)

        self.assertEqual(self.client.get("/get_all_orders_legacy").status_code, 401)

    def test_client_only_sees_own_orders(self):
        self._order(quantity=1)
        self.client.force_authenticate(self.other)
        self._order(quantity=1)

        body = self.client.get("/get_all_orders_legacy").json()

        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["user_id"], self.other.id)

    def test_admin_sees_all_orders(self):
        self._order(quantity=1)
        self.client.force_authenticate(self.other)
        self._order(quantity=1)
        self.client.force_authenticate(self.admin)

        body = self.client.get("/get_all_orders_legacy").json()

        self.assertEqual(len(body), 2)

    @patch("apps.orders.infrastructure.notifier.ThreadedLogNotifier._executor")
    def test_notification_is_sent_after_commit_without_blocking(self, executor):
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            response = self._order(quantity=1)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(callbacks), 1)
        executor.submit.assert_called_once()

    @patch("apps.orders.infrastructure.notifier.ThreadedLogNotifier._executor")
    def test_no_notification_when_order_is_rejected(self, executor):
        with self.captureOnCommitCallbacks(execute=True):
            self._order(quantity=100)

        executor.submit.assert_not_called()
