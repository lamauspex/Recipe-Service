"""
Publisher для событий User Service
"""

from backend.messaging.config import RabbitMQConfig
from backend.messaging.rabbit_mq_client import RabbitMQPublisher
import os
import logging
from datetime import datetime
from typing import Dict, Any
from uuid import UUID

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))


logger = logging.getLogger(__name__)


class UserEventPublisher:
    """Publisher для событий пользователей"""

    def __init__(self):
        self.rabbitmq_url = os.getenv(
            "RABBITMQ_URL", "amqp://admin:rabbitmq-password@localhost:5672/")
        self.publisher = RabbitMQPublisher(self.rabbitmq_url)
        self._connected = False

    async def connect(self):
        """Подключение к RabbitMQ"""
        try:
            if not self._connected:
                await self.publisher.connect()
                self._connected = True
                logger.info("UserEventPublisher connected to RabbitMQ")
        except Exception as e:
            logger.warning(f"Failed to connect to RabbitMQ: {e}")
            # Не прерываем работу, продолжаем без RabbitMQ

    async def disconnect(self):
        """Отключение от RabbitMQ"""
        if self._connected:
            try:
                await self.publisher.disconnect()
                self._connected = False
                logger.info("UserEventPublisher disconnected from RabbitMQ")
            except Exception as e:
                logger.warning(f"Error disconnecting from RabbitMQ: {e}")

    async def publish_user_created(self, user_data: Dict[str, Any]):
        """Публикация события создания пользователя"""
        if not self._connected:
            return

        try:
            event_data = {
                'event_type': 'user_created',
                'user_id': str(user_data['id']),
                'username': user_data['username'],
                'email': user_data['email'],
                'full_name': user_data.get('full_name', ''),
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'user-service'
            }

            await self._publish_event(
                exchange=RabbitMQConfig.USER_EVENTS,
                routing_key=RabbitMQConfig.USER_ROUTING_KEYS['user_created'],
                data=event_data
            )
        except Exception as e:
            logger.error(f"Failed to publish user_created event: {e}")

    async def publish_user_updated(
        self,
        user_id: UUID,
        updated_fields: Dict[str, Any]
    ):
        """Публикация события обновления пользователя"""
        if not self._connected:
            return

        try:
            event_data = {
                'event_type': 'user_updated',
                'user_id': str(user_id),
                'updated_fields': list(updated_fields.keys()),
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'user-service'
            }

            # Определяем тип обновления для routing key
            if 'profile' in updated_fields:
                routing_key = 'user.updated.profile'
            elif 'password' in updated_fields:
                routing_key = 'user.updated.password'
            elif 'email' in updated_fields:
                routing_key = 'user.updated.email'
            else:
                routing_key = 'user.updated.general'

            await self._publish_event(
                exchange=RabbitMQConfig.USER_EVENTS,
                routing_key=routing_key,
                data=event_data
            )
        except Exception as e:
            logger.error(f"Failed to publish user_updated event: {e}")

    async def publish_user_deleted(self, user_id: UUID):
        """Публикация события удаления пользователя"""
        if not self._connected:
            return

        try:
            event_data = {
                'event_type': 'user_deleted',
                'user_id': str(user_id),
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'user-service'
            }

            await self._publish_event(
                exchange=RabbitMQConfig.USER_EVENTS,
                routing_key=RabbitMQConfig.USER_ROUTING_KEYS['user_deleted'],
                data=event_data
            )
        except Exception as e:
            logger.error(f"Failed to publish user_deleted event: {e}")

    async def publish_user_login(self, user_id: UUID, username: str):
        """Публикация события входа пользователя"""
        if not self._connected:
            return

        try:
            event_data = {
                'event_type': 'user_login',
                'user_id': str(user_id),
                'username': username,
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'user-service'
            }

            await self._publish_event(
                exchange=RabbitMQConfig.USER_EVENTS,
                routing_key=RabbitMQConfig.USER_ROUTING_KEYS['user_login'],
                data=event_data
            )
        except Exception as e:
            logger.error(f"Failed to publish user_login event: {e}")

    async def publish_user_logout(self, user_id: UUID):
        """Публикация события выхода пользователя"""
        if not self._connected:
            return

        try:
            event_data = {
                'event_type': 'user_logout',
                'user_id': str(user_id),
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'user-service'
            }

            await self._publish_event(
                exchange=RabbitMQConfig.USER_EVENTS,
                routing_key=RabbitMQConfig.USER_ROUTING_KEYS['user_logout'],
                data=event_data
            )
        except Exception as e:
            logger.error(f"Failed to publish user_logout event: {e}")

    async def publish_user_premium_activated(self, user_id: UUID):
        """Публикация события активации premium"""
        if not self._connected:
            return

        try:
            event_data = {
                'event_type': 'user_premium_activated',
                'user_id': str(user_id),
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'user-service'
            }

            await self._publish_event(
                exchange=RabbitMQConfig.USER_EVENTS,
                routing_key=RabbitMQConfig.USER_ROUTING_KEYS['user_premium_activated'],
                data=event_data
            )
        except Exception as e:
            logger.error(
                f"Failed to publish user_premium_activated event: {e}")

    async def _publish_event(
        self,
        exchange: str,
        routing_key: str,
        data: Dict[str, Any]
    ):
        """Внутренний метод для публикации события"""
        try:
            if not self._connected:
                await self.connect()

            await self.publisher.publish_message(
                exchange_name=exchange,
                routing_key=routing_key,
                message=data,
                persistent=True
            )

            logger.info(
                f"Event published: {routing_key}"
                f" for user {data.get('user_id')}"
            )

        except Exception as e:
            logger.error(f"Failed to publish event {routing_key}: {e}")
            # В продакшене здесь можно добавить логику повторной попытки
            raise


# Глобальный экземпляр publisher'а
user_event_publisher = UserEventPublisher()
