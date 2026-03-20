"""
Lifespan для database_service
Управляет жизненным циклом приложения
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from backend.shared.logging.config import setup_logging
from backend.shared.logging.logger import get_logger
from .container import container


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan для FastAPI приложения

    Startup:
        - Проверка подключения к БД
        - Применение миграций (если AUTO_MIGRATE=true)

    Shutdown:
        - Закрытие соединений с БД
    """
    # Инициализация логирования при старте
    config = container.config()
    setup_logging(
        debug=config.DEBUG,
        json_output=config.LOG_FORMAT if hasattr(
            config, 'LOG_FORMAT') else False
    )

    logger = get_logger(__name__).bind(
        servicelayer="lifespan",
        service="database"
    )

    # Startup
    logger.info("Database Service starting...")
    connection_manager = container.connection_manager()

    if not connection_manager.test_connection():
        logger.error("Failed to connect to database")
        raise RuntimeError("Не удалось подключиться к базе данных")

    logger.info("Database connection successful")

    # Авто-миграции
    if os.getenv("AUTO_MIGRATE", "false").lower() == "true":
        logger.info("Running database migrations...")
        migration_runner = container.migration_runner()
        migration_runner.upgrade("head")
        logger.info("Migrations completed successfully")

    logger.info("Database Service started successfully")

    yield

    # Shutdown
    logger.info("Database Service shutting down...")
    connection_manager.close()
    logger.info("Database Service stopped")
