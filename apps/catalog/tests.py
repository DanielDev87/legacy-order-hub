from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.catalog.application.services import CatalogService
from apps.catalog.infrastructure.repositories import DjangoProductRepository
from apps.catalog.models import ProductModel
from apps.users.models import UserModel


def _bearer_header_for(user):
    token = RefreshToken.for_user(user).access_token
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


class CreateProductViewTests(APITestCase):
    def setUp(self):
        self.admin = UserModel.objects.create_user(
            username="admin_test", password="123456", role="admin"
        )
        self.client_user = UserModel.objects.create_user(
            username="client_test", password="123456", role="client"
        )
        self.payload = {"name": "Monitor", "price": 300.0, "stock": 4}

    def test_admin_can_create_product(self):
        response = self.client.post(
            "/products", self.payload, format="json", **_bearer_header_for(self.admin)
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(ProductModel.objects.filter(name="Monitor").exists())

    def test_non_admin_cannot_create_product(self):
        response = self.client.post(
            "/products",
            self.payload,
            format="json",
            **_bearer_header_for(self.client_user),
        )

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_request_is_rejected(self):
        response = self.client.post("/products", self.payload, format="json")

        self.assertEqual(response.status_code, 401)

    def test_invalid_payload_returns_400(self):
        response = self.client.post(
            "/products",
            {"name": "Sin precio"},
            format="json",
            **_bearer_header_for(self.admin),
        )

        self.assertEqual(response.status_code, 400)


class CatalogServiceTests(TestCase):
    def test_create_product_persists_via_repository(self):
        service = CatalogService(product_repository=DjangoProductRepository())

        product_id = service.create_product("Teclado", 45.0, 10)

        product = ProductModel.objects.get(id=product_id)
        self.assertEqual(product.name, "Teclado")
        self.assertEqual(product.stock, 10)

    def test_create_product_without_name_raises(self):
        service = CatalogService(product_repository=DjangoProductRepository())

        with self.assertRaises(ValueError):
            service.create_product("", 10.0, 1)
