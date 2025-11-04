"""
Publisher для событий Recipe Service
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any
from uuid import UUID

from backend.messaging.rabbit_mq_client import RabbitMQPublisher
from backend.messaging.config import RabbitMQConfig

logger = logging.getLogger(__name__)


class RecipeEventPublisher:
    """Publisher для событий рецептов"""

    def __init__(self):
        self.rabbitmq_url = os.getenv("RABBITMQ_URL")
        self.publisher = RabbitMQPublisher(self.rabbitmq_url)
        self._connected = False

    async def connect(self):
        """Подключение к RabbitMQ"""
        if not self._connected:
            await self.publisher.connect()
            self._connected = True
            logger.info("RecipeEventPublisher connected to RabbitMQ")

    async def disconnect(self):
        """Отключение от RabbitMQ"""
        if self._connected:
            await self.publisher.disconnect()
            self._connected = False
            logger.info("RecipeEventPublisher disconnected from RabbitMQ")

    async def publish_recipe_created(
        self,
        recipe_data: Dict[str, Any]
    ):
        """Публикация события создания рецепта"""
        event_data = {
            'event_type': 'recipe_created',
            'recipe_id': str(recipe_data['id']),
            'author_id': str(recipe_data['author_id']),
            'title': recipe_data['title'],
            'description': recipe_data.get('description', ''),
            'difficulty': recipe_data.get('difficulty', 'medium'),
            'cooking_time': recipe_data.get('cooking_time', 0),
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'recipe-service'
        }

        await self._publish_event(
            exchange=RabbitMQConfig.RECIPE_EVENTS,
            routing_key=RabbitMQConfig.RECIPE_ROUTING_KEYS['recipe_created'],
            data=event_data
        )

    async def publish_recipe_updated(
        self,
        recipe_id: UUID,
        updated_fields: Dict[str, Any]
    ):
        """Публикация события обновления рецепта"""
        event_data = {
            'event_type': 'recipe_updated',
            'recipe_id': str(recipe_id),
            'updated_fields': list(updated_fields.keys()),
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'recipe-service'
        }

        await self._publish_event(
            exchange=RabbitMQConfig.RECIPE_EVENTS,
            routing_key=RabbitMQConfig.RECIPE_ROUTING_KEYS['recipe_updated'],
            data=event_data
        )

    async def publish_recipe_deleted(
        self,
        recipe_id: UUID,
        author_id: UUID
    ):
        """Публикация события удаления рецепта"""
        event_data = {
            'event_type': 'recipe_deleted',
            'recipe_id': str(recipe_id),
            'author_id': str(author_id),
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'recipe-service'
        }

        await self._publish_event(
            exchange=RabbitMQConfig.RECIPE_EVENTS,
            routing_key=RabbitMQConfig.RECIPE_ROUTING_KEYS['recipe_deleted'],
            data=event_data
        )

    async def publish_recipe_rated(
        self,
        recipe_id: UUID,
        user_id: UUID,
        rating: int
    ):
        """Публикация события оценки рецепта"""
        event_data = {
            'event_type': 'recipe_rated',
            'recipe_id': str(recipe_id),
            'user_id': str(user_id),
            'rating': rating,
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'recipe-service'
        }

        await self._publish_event(
            exchange=RabbitMQConfig.RECIPE_EVENTS,
            routing_key=RabbitMQConfig.RECIPE_ROUTING_KEYS['recipe_rated'],
            data=event_data
        )

    async def publish_recipe_commented(
        self,
        recipe_id: UUID,
        user_id: UUID,
        comment_id: UUID
    ):
        """Публикация события комментария к рецепту"""
        event_data = {
            'event_type': 'recipe_commented',
            'recipe_id': str(recipe_id),
            'user_id': str(user_id),
            'comment_id': str(comment_id),
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'recipe-service'
        }

        await self._publish_event(
            exchange=RabbitMQConfig.RECIPE_EVENTS,
            routing_key=RabbitMQConfig.RECIPE_ROUTING_KEYS['recipe_commented'],
            data=event_data
        )

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
                f" for recipe {data.get('recipe_id')}"
            )

        except Exception as e:
            logger.error(f"Failed to publish event {routing_key}: {e}")
            # В продакшене здесь можно добавить логику повторной попытки
            raise


# Глобальный экземпляр publisher'а
recipe_event_publisher = RecipeEventPublisher()
