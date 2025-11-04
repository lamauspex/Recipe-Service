"""
Тесты для системы событий пользователей
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from backend.services.user_service.src.events.publishers import (
    user_event_publisher,
    UserEventPublisher
)
from backend.services.user_service.src.services.user_service import UserService
from backend.services.user_service.schemas.schemas import UserCreate
from backend.services.user_service.src.database.connection import (
    get_db_session)
from backend.messaging.rabbit_mq_client import RabbitMQPublisher


class TestUserEventPublisher:
    """Тесты для издателя событий пользователей"""

    @pytest.fixture
    def mock_rabbitmq(self):
        """Мок RabbitMQ издателя"""
        mock_publisher = AsyncMock()
        mock_publisher.publish = AsyncMock()
        return mock_publisher

    @pytest.fixture
    def publisher_with_mock(self, mock_rabbitmq):
        """Издатель с замоканным RabbitMQ"""
        publisher = UserEventPublisher()
        publisher.publisher = mock_rabbitmq
        return publisher

    def test_publish_user_created(self, publisher_with_mock):
        """Тест публикации события создания пользователя"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        email = "test@example.com"

        # Запускаем асинхронную публикацию
        asyncio.run(publisher_with_mock.publish_user_created(user_id, email))

        # Проверяем, что publish был вызван с правильными данными
        publisher_with_mock.publisher.publish.assert_called_once()
        call_args = publisher_with_mock.publisher.publish.call_args

        assert call_args[0][0] == "user.created"
        event_data = call_args[0][1]
        assert event_data["user_id"] == user_id
        assert event_data["email"] == email
        assert "timestamp" in event_data

    def test_publish_user_updated(self, publisher_with_mock):
        """Тест публикации события обновления пользователя"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        email = "test@example.com"

        asyncio.run(publisher_with_mock.publish_user_updated(user_id, email))

        publisher_with_mock.publisher.publish.assert_called_once()
        call_args = publisher_with_mock.publisher.publish.call_args

        assert call_args[0][0] == "user.updated"
        event_data = call_args[0][1]
        assert event_data["user_id"] == user_id
        assert event_data["email"] == email
        assert "timestamp" in event_data

    def test_publish_user_deleted(self, publisher_with_mock):
        """Тест публикации события удаления пользователя"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        asyncio.run(publisher_with_mock.publish_user_deleted(user_id))

        publisher_with_mock.publisher.publish.assert_called_once()
        call_args = publisher_with_mock.publisher.publish.call_args

        assert call_args[0][0] == "user.deleted"
        event_data = call_args[0][1]
        assert event_data["user_id"] == user_id
        assert "timestamp" in event_data

    def test_publish_user_login(self, publisher_with_mock):
        """Тест публикации события входа пользователя"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        email = "test@example.com"
        ip_address = "192.168.1.1"

        asyncio.run(publisher_with_mock.publish_user_login(
            user_id, email, ip_address))

        publisher_with_mock.publisher.publish.assert_called_once()
        call_args = publisher_with_mock.publisher.publish.call_args

        assert call_args[0][0] == "user.login"
        event_data = call_args[0][1]
        assert event_data["user_id"] == user_id
        assert event_data["email"] == email
        assert event_data["ip_address"] == ip_address
        assert "timestamp" in event_data


@pytest.mark.asyncio
async def test_user_service_integration_with_events():
    """Интеграционный тест UserService с событиями"""
    # Создаем тестовые данные
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }

    user_create = UserCreate(**user_data)

    # Мокаем издателя событий
    with patch.object(
            user_event_publisher,
            'publish_user_created') as mock_publish:
        mock_publish.return_value = None

        # Получаем сессию БД
        db = next(get_db_session())

        try:
            # Создаем сервис
            user_service = UserService(db)

            # Создаем пользователя
            result = user_service.create_user(user_create)

            # Проверяем результат
            assert result["email"] == user_data["email"]
            assert result["first_name"] == user_data["first_name"]

            # Проверяем, что событие было опубликовано
            mock_publish.assert_called_once()

        finally:
            db.close()


@pytest.mark.asyncio
async def test_rabbitmq_end_to_end():
    """Энд-энд тест RabbitMQ"""
    # Мокаем RabbitMQ
    mock_connection = AsyncMock()
    mock_channel = AsyncMock()
    mock_connection.channel.return_value = mock_channel

    with patch('aio_pika.connect_robust', return_value=mock_connection):
        # Создаем издатель
        publisher = RabbitMQPublisher()

        # Подключаемся
        await publisher.connect()

        # Создаем издатель событий
        event_publisher = UserEventPublisher()
        event_publisher.publisher = publisher

        # Публикуем событие
        await event_publisher.publish_user_created(
            "test-id", "test@example.com"
        )

        # Проверяем, что сообщение было отправлено
        assert mock_channel.default_exchange.publish.called
