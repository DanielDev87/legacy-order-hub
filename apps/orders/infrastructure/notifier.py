import logging
from concurrent.futures import ThreadPoolExecutor

from apps.orders.domain.entities import Order
from apps.orders.domain.ports import NotificationPort

logger = logging.getLogger("orderhub.notifications")


class ThreadedLogNotifier(NotificationPort):
    """Notifica en un hilo aparte para no bloquear la respuesta HTTP."""

    _executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="notifier")

    def order_created(self, order: Order) -> None:
        self._executor.submit(self._send, order)

    @staticmethod
    def _send(order: Order) -> None:
        logger.info(
            "Notificación de orden creada",
            extra={
                "event": "order_created",
                "order_id": order.id,
                "user_id": order.user_id,
                "total": order.total,
            },
        )
