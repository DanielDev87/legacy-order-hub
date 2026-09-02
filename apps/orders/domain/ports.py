import abc

from apps.orders.domain.entities import Order


class OrderRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def create(
        self, user_id: int, product_id: int, quantity: int, total: float, status: str
    ) -> int: ...

    @abc.abstractmethod
    def list_all(self) -> list[Order]: ...
