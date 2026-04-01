"""Publisher для отправки событий в RabbitMQ"""

import json
import aio_pika
from typing import Optional

from backend.service_recipe.src.config.config_grpc import get_settings


class MessagePublisher:
    """Publisher для RabbitMQ"""

    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self._connection: Optional[aio_pika.Connection] = None
        self._channel: Optional[aio_pika.Channel] = None

    async def connect(self):
        """Установка соединения с RabbitMQ"""
        self._connection = await aio_pika.connect_robust(self.connection_url)
        self._channel = await self._connection.channel()

    async def close(self):
        """Закрытие соединения"""
        if self._connection:
            await self._connection.close()

    async def publish_recipe_created(self, recipe_data: dict):
        """Отправка события о создании рецепта"""
        if not self._channel:
            await self.connect()

        # Объявляем exchange и queue
        exchange = await self._channel.declare_exchange(
            "recipe_events",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        message = aio_pika.Message(
            body=json.dumps(recipe_data).encode(),
            content_type="application/json"
        )

        await exchange.publish(
            message,
            routing_key="recipe.created"
        )


# Глобальный экземпляр
_publisher: Optional[MessagePublisher] = None


def get_message_publisher() -> MessagePublisher:
    """Dependency для получения publisher"""
    global _publisher
    settings = get_settings()

    if _publisher is None:
        _publisher = MessagePublisher(settings.RABBITMQ_URL)

    return _publisher
