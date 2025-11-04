"""
Consumer для обработки событий в Recipe Service
"""

import os
import logging
from typing import Dict, Any

from backend.messaging.rabbit_mq_client import (
    BaseEventHandler, RabbitMQConsumer)
from backend.messaging.config import RabbitMQConfig
from backend.services.recipe_service.src.services.recipe_service import (
    RecipeService)


logger = logging.getLogger(__name__)


class UserEventHandler(BaseEventHandler):
    """Обработчик событий пользователей"""

    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    async def handle(
        self,
        data: Dict[str, Any],
        routing_key: str,
        headers: Dict[str, Any]
    ):
        """Обработка события пользователя"""
        try:
            if routing_key == 'user.deleted':
                await self._handle_user_deleted(data)
            elif routing_key.startswith('user.updated.'):
                await self._handle_user_updated(data, routing_key)
            else:
                logger.info(f"Unhandled user event: {routing_key}")

        except Exception as e:
            logger.error(f"Error handling user event {routing_key}: {e}")
            raise

    async def _handle_user_deleted(self, data: Dict[str, Any]):
        """Обработка удаления пользователя"""
        user_id = data.get('user_id')
        if not user_id:
            logger.error("No user_id in user_deleted event")
            return

        logger.info(f"Processing user_deleted event for user {user_id}")

        # Здесь можно добавить логику:
        # - Скрыть рецепты удаленного пользователя
        # - Удалить или анонимизировать комментарии
        # - Обновить статистику

        with self.db_session_factory() as db:
            recipe_service = RecipeService(db)
            # Мягкое удаление рецептов пользователя
            deleted_count = recipe_service.soft_delete_user_recipes(user_id)
            logger.info(
                f"Soft deleted {deleted_count} recipes for user {user_id}")

    async def _handle_user_updated(
        self,
        data: Dict[str, Any],
        routing_key: str
    ):
        """Обработка обновления пользователя"""
        user_id = data.get('user_id')
        updated_fields = data.get('updated_fields', [])

        if not user_id:
            logger.error("No user_id in user_updated event")
            return

        logger.info(
            f"Processing user_updated event for user {user_id},"
            f" updated fields: {updated_fields}"
        )

        # Здесь будет логика :
        # - Обновить имя автора в рецептах
        # - Изменить видимость рецептов при смене статуса

        if 'profile' in updated_fields or 'full_name' in updated_fields:
            # Обновление имени автора в рецептах
            await self._update_author_name_in_recipes(user_id)

    async def _update_author_name_in_recipes(self, user_id: str):
        """Обновление имени автора в рецептах"""

        with self.db_session_factory() as db:
            recipe_service = RecipeService(db)
            # Здесь будет логика обновления имени автора
            # recipe_service.update_author_name(user_id, new_name)
            logger.info(f"Would update author name for user {user_id} recipes")


class RecipeEventConsumer:
    """Consumer для Recipe Service"""

    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.rabbitmq_url = os.getenv("RABBITMQ_URL")
        self.consumer = RabbitMQConsumer(self.rabbitmq_url)
        self.user_event_handler = UserEventHandler(db_session_factory)

    async def start_consuming(self):
        """Запуск потребления сообщений"""
        try:
            await self.consumer.connect()

            # Настройка очередей для Recipe Service
            queues = RabbitMQConfig.RECIPE_SERVICE_QUEUES

            for queue_config in queues:
                queue_name = queue_config['name']
                exchange_name = queue_config['exchange']
                routing_key = queue_config['routing_key']

                logger.info(f"Starting consumer for queue: {queue_name}")

                # Запуск потребления в отдельной задаче
                import asyncio
                asyncio.create_task(
                    self.consumer.consume_messages(
                        queue_name=queue_name,
                        callback=self.user_event_handler,
                        exchange_name=exchange_name,
                        routing_key=routing_key,
                        auto_ack=False
                    )
                )

                # Объявление очереди и привязка
                await self.consumer.declare_queue(queue_name)
                await self.consumer.bind_queue(
                    queue_name,
                    exchange_name,
                    routing_key
                )

            logger.info("Recipe Service consumers started")

        except Exception as e:
            logger.error(f"Failed to start consumers: {e}")
            raise

    async def stop_consuming(self):
        """Остановка потребления сообщений"""
        try:
            await self.consumer.disconnect()
            logger.info("Recipe Service consumers stopped")
        except Exception as e:
            logger.error(f"Error stopping consumers: {e}")


# Глобальный экземпляр consumer'а
recipe_event_consumer = None


async def start_recipe_consumers(db_session_factory):
    """Запуск потребителей для Recipe Service"""
    global recipe_event_consumer
    recipe_event_consumer = RecipeEventConsumer(db_session_factory)
    await recipe_event_consumer.start_consuming()


async def stop_recipe_consumers():
    """Остановка потребителей для Recipe Service"""
    global recipe_event_consumer
    if recipe_event_consumer:
        await recipe_event_consumer.stop_consuming()
