"""
Lifecycle management for Recipe Service

Управляет только:
- Alembic миграциями
- Подключением к базе данных

Остальные инициализации (gRPC, RabbitMQ) происходят в dependencies
"""


from contextlib import asynccontextmanager
from fastapi import FastAPI
from alembic import command
from alembic.config import Config

from backend.shared.logging import get_logger
from backend.shared.database import ConnectionManager, DataBaseConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Управление жизненным циклом приложения """

    logger = get_logger(__name__).bind(
        layer="lifespan",
        service="recipe"
    )

    # Запускаем миграции при старте
    alembic_cfg = Config("backend/service_recipe/migration/alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info(">>> Migration Recipe_service успех")

    # Проверяем подключение к базе данных
    config = DataBaseConfig()
    connection_manager = ConnectionManager(config)

    if not connection_manager.test_connection():
        logger.error("Failed to connect to database")
        raise Exception("Не удалось подключиться к базе данных")

    logger.info("Database connection successful")

    logger.info(
        "Recipe Service started",
        docs_url="http://127.0.0.1:8001/docs",
        redoc_url="http://127.0.0.1:8001/redoc",
        health_url="http://127.0.0.1:8001/health"
    )

    yield

    logger.info("Recipe Service shutdown complete")
