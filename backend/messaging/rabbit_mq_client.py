"""
Бовый клиент RabbitMQ с поддержкой подключения и управления
"""

import asyncio
import json
import logging
from abc import abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Callable, Dict, Optional

import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractChannel

logger = logging.getLogger(__name__)


class RabbitMQClient:
    """Бовый клиент RabbitMQ с поддержкой подключения и управления"""

    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.connection: Optional[AbstractRobustConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self._is_connected = False

    async def connect(self):
        """Установка подключения к RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(
                self.connection_url,
                timeout=10,
                reconnect_interval=5,
                timeout_reconnect_attempts=3
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)
            self._is_connected = True
            logger.info("RabbitMQ connection established")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self):
        """Закрытие подключения"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            self._is_connected = False
            logger.info("RabbitMQ connection closed")

    @asynccontextmanager
    async def get_channel(self):
        """Контекст менеджер для получения канала"""
        if not self._is_connected:
            await self.connect()

        try:
            yield self.channel
        except Exception as e:
            logger.error(f"Channel error: {e}")
            raise

    async def declare_exchange(
        self,
        name: str,
        exchange_type: str = 'direct',
        durable: bool = True
    ):
        """Создание exchange"""
        async with self.get_channel() as channel:
            exchange = await channel.declare_exchange(
                name=name,
                type=exchange_type,
                durable=durable
            )
            logger.info(f"Exchange '{name}' declared")
            return exchange

    async def declare_queue(
        self,
        name: str,
        durable: bool = True,
        exclusive: bool = False
    ):
        """Создание очереди"""
        async with self.get_channel() as channel:
            queue = await channel.declare_queue(
                name=name,
                durable=durable,
                exclusive=exclusive
            )
            logger.info(f"Queue '{name}' declared")
            return queue

    async def bind_queue(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str
    ):
        """Привязка очереди к exchange"""
        async with self.get_channel() as channel:
            queue = await channel.declare_queue(queue_name, durable=True)
            exchange = await self.declare_exchange(exchange_name)
            await queue.bind(exchange, routing_key)
            logger.info(
                f"Queue '{queue_name}' bound to exchange"
                "'{exchange_name}' with routing key '{routing_key}'"
            )


class RabbitMQPublisher(RabbitMQClient):
    """Publisher для отправки сообщений"""

    async def publish_message(
        self,
        exchange_name: str,
        routing_key: str,
        message: Dict[str, Any],
        headers: Optional[Dict[str, Any]] = None,
        persistent: bool = True
    ):
        """Публикация сообщения"""
        try:
            async with self.get_channel() as channel:
                exchange = await channel.declare_exchange(
                    exchange_name,
                    type='topic',
                    durable=True
                )

                message_body = json.dumps(message, default=str).encode()

                properties = aio_pika.BasicProperties(
                    delivery_mode=2 if persistent else 1,
                    headers=headers or {},
                    content_type='application/json',
                    message_id=str(message.get('id', '')),
                    timestamp=message.get('timestamp')
                )

                await exchange.publish(
                    aio_pika.Message(
                        body=message_body,
                        properties=properties
                    ),
                    routing_key=routing_key
                )

                logger.info(
                    f"Message published to exchange "
                    f"'{exchange_name}' with routing key '{routing_key}'"
                )

        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise


class RabbitMQConsumer(RabbitMQClient):
    """Consumer для приема сообщений"""

    async def consume_messages(
        self,
        queue_name: str,
        callback: Callable,
        exchange_name: str,
        routing_key: str,
        auto_ack: bool = False
    ):
        """Начать потребление сообщений"""
        try:
            async with self.get_channel() as channel:
                # Объявление exchange
                exchange = await channel.declare_exchange(
                    exchange_name,
                    type='topic',
                    durable=True
                )

                # Объявление очереди
                queue = await channel.declare_queue(
                    queue_name,
                    durable=True
                )

                # Привязка очереди к exchange
                await queue.bind(exchange, routing_key)

                logger.info(f"Starting consumer for queue '{queue_name}'")

                async def message_processor(message: aio_pika.IncomingMessage):
                    """Обработка входящего сообщения"""
                    async with message.process():
                        try:
                            body = message.body.decode()
                            data = json.loads(body)

                            logger.info(
                                f"Received message from routing key"
                                f"'{message.routing_key}': {data}"
                            )

                            # Вызов callback функции
                            await callback(
                                data,
                                message.routing_key,
                                message.headers
                            )

                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            if not auto_ack:
                                await message.nack(requeue=False)

                # Начало потребления
                await queue.consume(message_processor, no_ack=auto_ack)

                # Бесконечное ожидание сообщений
                logger.info(f"Consumer started for queue '{queue_name}'")
                await asyncio.Future()

        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise


class BaseEventHandler:
    """Бовый класс для обработчиков событий"""

    @abstractmethod
    async def handle(
        self,
        data: Dict[str, Any],
        routing_key: str,
        headers: Optional[Dict[str, Any]]
    ):
        """Обработка события"""
        pass

    async def __call__(
        self,
        data: Dict[str, Any],
        routing_key: str,
        headers: Optional[Dict[str, Any]]
    ):
        """Вызов обработчика"""
        await self.handle(data, routing_key, headers)
