from rest_framework.test import APITestCase

from apps.catalog.models import ProductModel
from apps.users.models import UserModel


class OrdersApiTests(APITestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testuser", password="123456"
        )
        self.product = ProductModel.objects.create(
            name="Mouse USB", price=15.50, stock=5
        )

    def test_create_order_success(self):
        response = self.client.post(
            "/create_order",
            {"user_id": self.user.id, "product_id": self.product.id, "quantity": 2},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["total"], 31.0)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

    def test_create_order_insufficient_stock_returns_400(self):
        response = self.client.post(
            "/create_order",
            {"user_id": self.user.id, "product_id": self.product.id, "quantity": 100},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_create_order_product_not_found_returns_404(self):
        response = self.client.post(
            "/create_order",
            {"user_id": self.user.id, "product_id": 9999, "quantity": 1},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_get_all_orders_legacy_returns_created_orders(self):
        self.client.post(
            "/create_order",
            {"user_id": self.user.id, "product_id": self.product.id, "quantity": 1},
            format="json",
        )

        response = self.client.get("/get_all_orders_legacy")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["product_id"], self.product.id)
