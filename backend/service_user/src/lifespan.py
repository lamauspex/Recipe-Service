"""
Управление жизненным циклом приложения User Service
"""

import os

from contextlib import asynccontextmanager
from fastapi import FastAPI, logger

from backend.service_migreation.src import (
    get_connection_manager
)
from backend.service_user.src.container import container
from backend.shared.logging.config import setup_logging
from backend.shared.logging.logger import get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """

    # Код запуска
    await startup_handler()
    yield

    # Код завершения
    await shutdown_handler()


async def startup_handler():
    """Обработчик запуска приложения"""

    logger = get_logger(__name__).bind(
        layer="lifespan",
        service="user"
    )

    monitoring_config = container.monitoring_config()
    setup_logging(
        debug=monitoring_config.DEBUG,
        json_output=monitoring_config.LOG_FORMAT
    )
    logger.info("User Service запущен")

    # Пропускаем инициализацию в тестах
    if os.environ.get("TESTING") == "1" or os.environ.get(
            "USER_SERVICE_TESTING") == "1":
        return

    # Получаем connection_manager и migration_runner из database_service
    connection_manager = get_connection_manager()

    # Проверяем подключение к базе данных
    if not connection_manager.test_connection():
        logger.error("Failed to connect to database")
        raise Exception("Не удалось подключиться к базе данных")

    logger.info("Database connection successful")
    logger.info("Database initialized successfully")
    logger.info(
        "User Service started",
        docs_url="http://127.0.0.1:8000/docs",
        redoc_url="http://127.0.0.1:8000/redoc",
        health_url="http://127.0.0.1:8000/health"
    )


async def shutdown_handler():
    """Обработчик завершения приложения"""
    logger.info("User Service процесс завершён")
