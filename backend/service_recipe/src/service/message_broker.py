""" Publisher для отправки событий в RabbitMQ """

import json
import asyncio
import aio_pika
from typing import Optional


class MessagePublisher:
    """Publisher для RabbitMQ"""

    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self._connection: Optional[aio_pika.Connection] = None
        self._channel: Optional[aio_pika.Channel] = None
        self._lock = asyncio.Lock()

    async def connect(self):
        """Установка соединения с RabbitMQ"""
        if self._connection and not self._connection.is_closed:
            return

        self._connection = await aio_pika.connect_robust(
            self.connection_url,
            timeout=10
        )
        self._channel = await self._connection.channel()

        # Делаем канал устойчивым к ошибкам
        await self._channel.set_qos(prefetch_count=10)

    async def _ensure_connected(self):
        """Гарантирует подключение перед отправкой"""
        async with self._lock:
            if not self._channel or self._channel.is_closed:
                await self.connect()

    async def publish_recipe_created(self, recipe_data: dict):
        """Отправка события о создании рецепта"""
        await self._ensure_connected()

        exchange = await self._channel.declare_exchange(
            "recipe_events",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        message = aio_pika.Message(
            body=json.dumps(recipe_data).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT  # важно для durability
        )

        await exchange.publish(
            message,
            routing_key="recipe.created"
        )

    async def close(self):
        """Закрытие соединения"""
        async with self._lock:
            if self._connection and not self._connection.is_closed:
                await self._connection.close()
                self._connection = None
                self._channel = None
