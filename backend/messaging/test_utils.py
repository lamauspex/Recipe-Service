"""
Утилиты для тестирования RabbitMQ функциональности
"""


import logging
from typing import Any, Dict, List, Optional

from backend.messaging.rabbit_mq_client import (
    RabbitMQConsumer, RabbitMQPublisher)


logger = logging.getLogger(__name__)


class MockRabbitMQClient:
    """Mock клиент для тестирования"""

    def __init__(self):
        self.published_messages = []
        self.consumed_messages = []
        self.exchanges = set()
        self.queues = set()
        self.bindings = []

    async def connect(self):
        """Mock подключения"""
        logger.info("Mock RabbitMQ connected")

    async def disconnect(self):
        """Mock отключения"""
        logger.info("Mock RabbitMQ disconnected")

    async def declare_exchange(
        self,
        name: str,
        exchange_type: str = 'direct',
        durable: bool = True
    ):
        """Mock объявления exchange"""
        self.exchanges.add(name)
        logger.info(f"Mock exchange '{name}' declared")

    async def declare_queue(
        self,
        name: str,
        durable: bool = True,
        exclusive: bool = False
    ):
        """Mock объявления очереди"""
        self.queues.add(name)
        logger.info(f"Mock queue '{name}' declared")

    async def bind_queue(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str
    ):
        """Mock привязки очереди"""
        self.bindings.append((queue_name, exchange_name, routing_key))
        logger.info(
            f"Mock binding created:"
            f"{queue_name} -> {exchange_name} ({routing_key})"
        )


class MockRabbitMQPublisher(MockRabbitMQClient):
    """Mock publisher для тестирования"""

    async def publish_message(
        self,
        exchange_name: str,
        routing_key: str,
        message: Dict[str, Any],
        headers: Optional[Dict[str, Any]] = None,
        persistent: bool = True
    ):
        """Mock публикации сообщения"""
        self.published_messages.append({
            'exchange': exchange_name,
            'routing_key': routing_key,
            'message': message,
            'headers': headers,
            'persistent': persistent
        })
        logger.info(
            f"Mock message published to {exchange_name}"
            f" with routing key {routing_key}"
        )


class MockRabbitMQConsumer(MockRabbitMQClient):
    """Mock consumer для тестирования"""

    def __init__(self):
        super().__init__()
        self.callbacks = {}

    async def consume_messages(
        self,
        queue_name: str,
        callback,
        exchange_name: str,
        routing_key: str,
        auto_ack: bool = False
    ):
        """Mock потребления сообщений"""
        self.callbacks[queue_name] = callback
        logger.info(f"Mock consumer started for queue '{queue_name}'")

    async def simulate_message(
        self,
        queue_name: str,
        data: Dict[str, Any],
        routing_key: str
    ):
        """Симуляция получения сообщения"""
        if queue_name in self.callbacks:
            await self.callbacks[queue_name](data, routing_key, {})
            self.consumed_messages.append({
                'queue': queue_name,
                'data': data,
                'routing_key': routing_key
            })


class RabbitMQTestHelper:
    """Хелпер для тестирования RabbitMQ"""

    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.publisher = None
        self.consumer = None

    async def setup(self, connection_url: str = "mock://localhost"):
        """Настройка тестового окружения"""
        if self.use_mock:
            self.publisher = MockRabbitMQPublisher()
            self.consumer = MockRabbitMQConsumer()
        else:
            # Для интеграционных тестов можно использовать реальный RabbitMQ
            self.publisher = RabbitMQPublisher(connection_url)
            self.consumer = RabbitMQConsumer(connection_url)
            await self.publisher.connect()
            await self.consumer.connect()

    async def cleanup(self):
        """Очистка тестового окружения"""
        if not self.use_mock:
            if self.publisher:
                await self.publisher.disconnect()
            if self.consumer:
                await self.consumer.disconnect()

    async def publish_test_event(
        self,
        exchange: str,
        routing_key: str,
        event_data: Dict[str, Any]
    ):
        """Публикация тестового события"""
        await self.publisher.publish_message(exchange, routing_key, event_data)

    def get_published_messages(self) -> List[Dict]:
        """Получить все опубликованные сообщения"""
        return self.publisher.published_messages if self.publisher else []

    def get_consumed_messages(self) -> List[Dict]:
        """Получить все потребленные сообщения"""
        return self.consumer.consumed_messages if self.consumer else []

    async def simulate_event_consumption(
        self,
        queue_name: str,
        event_data: Dict[str, Any],
        routing_key: str
    ):
        """Симулировать потребление события (только для mock)"""
        if self.use_mock and self.consumer:
            await self.consumer.simulate_message(
                queue_name,
                event_data,
                routing_key
            )


class TestEventValidator:
    """Валидатор событий для тестов"""

    @staticmethod
    def validate_user_created_event(data: Dict[str, Any]) -> bool:
        """Валидация события создания пользователя"""
        required_fields = ['user_id', 'username',
                           'email', 'timestamp', 'event_type']
        return all(field in data for field in required_fields)

    @staticmethod
    def validate_recipe_created_event(data: Dict[str, Any]) -> bool:
        """Валидация события создания рецепта"""
        required_fields = ['recipe_id', 'author_id',
                           'title', 'timestamp', 'event_type']
        return all(field in data for field in required_fields)

    @staticmethod
    def validate_event_structure(data: Dict[str, Any]) -> bool:
        """Базовая валидация структуры события"""
        return 'event_type' in data and 'timestamp' in data


# Фикстуры для pytest
async def get_test_rabbitmq():
    """Получить тестовый RabbitMQ клиент"""
    helper = RabbitMQTestHelper(use_mock=True)
    await helper.setup()
    yield helper
    await helper.cleanup()


# Пример использования в тестах
"""
@pytest.mark.asyncio
async def test_user_created_event():
    test_helper = RabbitMQTestHelper(use_mock=True)
    await test_helper.setup()

    # Публикация события
    event_data = {
        'user_id': '123',
        'username': 'testuser',
        'email': 'test@example.com',
        'timestamp': '2024-01-01T00:00:00Z',
        'event_type': 'user_created'
    }

    await test_helper.publish_test_event(
        'user_events',
        'user.created',
        event_data
        )

    # Проверка
    messages = test_helper.get_published_messages()
    assert len(messages) == 1
    assert messages[0]['routing_key'] == 'user.created'
    assert TestEventValidator.validate_user_created_event(messages[0]['message'])

    await test_helper.cleanup()
"""
