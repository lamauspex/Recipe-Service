"""
Управление жизненным циклом приложения User Service
"""

import os

from contextlib import asynccontextmanager
from fastapi import FastAPI
from alembic import command
from alembic.config import Config

from backend.shared.database import ConnectionManager, DataBaseConfig
from backend.service_user.src.container import container
from backend.shared.logging.config import setup_logging
from backend.shared.logging.logger import get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Управление жизненным циклом приложения """

    # Запускаем миграции при старте
    alembic_cfg = Config("backend/service_user/migration/alembic.ini")
    command.upgrade(alembic_cfg, "head")

    # Код запуска
    await startup_handler()
    yield

    # Код завершения
    await shutdown_handler()


async def startup_handler():
    """ Обработчик запуска приложения """

    config = DataBaseConfig()
    connection_manager = ConnectionManager(config)

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

    # Проверяем подключение к базе данных
    if not connection_manager.test_connection():
        logger.error("Failed to connect to database")
        raise Exception("Не удалось подключиться к базе данных")

    logger.info("Database connection successful")
    logger.info("Database initialized successfully")
    logger.info(
        "User Service started\n",
        docs_url="http://127.0.0.1:8000/docs\n",
        redoc_url="http://127.0.0.1:8000/redoc\n",
        health_url="http://127.0.0.1:8000/health\n"
    )


async def shutdown_handler():
    """Обработчик завершения приложения"""
    logger = get_logger(__name__).bind(
        layer="lifespan",
        service="user"
    )
    logger.info("User Service процесс завершён")
