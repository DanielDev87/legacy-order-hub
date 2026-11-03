from django.db import transaction

from apps.catalog.domain.exceptions import ProductNotFoundError
from apps.catalog.domain.ports import ProductRepositoryPort
from apps.orders.domain.entities import Order
from apps.orders.domain.exceptions import InsufficientStockError
from apps.orders.domain.ports import OrderRepositoryPort


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        product_repository: ProductRepositoryPort,
    ):
        self._order_repository = order_repository
        self._product_repository = product_repository

    @transaction.atomic
    def create_order(self, user_id: int, product_id: int, quantity: int) -> Order:
        product = self._product_repository.get_by_id_for_update(product_id)
        if product is None:
            raise ProductNotFoundError("Producto no encontrado")

        if product.stock < quantity:
            raise InsufficientStockError("Stock insuficiente")

        total = product.price * quantity
        order_id = self._order_repository.create(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total=total,
            status="PENDING",
        )

        self._product_repository.update_stock(product_id, product.stock - quantity)

        print(f"[LOG LEGADO]: Notificando correo para la orden ID: {order_id}...")

        return Order(
            id=order_id,
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total=total,
            status="PENDING",
        )

    def list_orders(self) -> list[Order]:
        return self._order_repository.list_all()

    def list_orders_by_user(self, user_id: int) -> list[Order]:
        return self._order_repository.list_by_user(user_id)
