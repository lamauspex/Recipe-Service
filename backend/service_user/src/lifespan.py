"""
Управление жизненным циклом приложения User Service

Отвечает ТОЛЬКО за:
- Миграции базы данных
- Подключение к БД
- Очистку при завершении

"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from alembic import command
from alembic.config import Config

from backend.shared.database import ConnectionManager, DataBaseConfig
from backend.service_user.src.infrastructure import container
from backend.shared.logging.config import setup_logging
from backend.shared.logging.logger import get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Управление жизненным циклом приложения """

    logger = get_logger(__name__).bind(
        layer="lifespan",
        service="user"
    )

    # Запускаем миграции при старте
    alembic_cfg = Config("backend/service_user/migration/alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info(">>> Миграции выполнены")

    # Инициализация подключения к БД
    config = DataBaseConfig()
    connection_manager = ConnectionManager(config)

    # Пропускаем в тестах
    if os.environ.get("TESTING") == "1" or os.environ.get(
            "USER_SERVICE_TESTING") == "1":
        yield
        return

    # Проверяем подключение к БД
    if not connection_manager.test_connection():
        logger.error("Failed to connect to database")
        raise Exception("Не удалось подключиться к базе данных")

    logger.info("DB Подключена")

    # Настройка логирования
    monitoring_config = container.monitoring_config()
    setup_logging(
        debug=monitoring_config.DEBUG,
        json_output=monitoring_config.LOG_FORMAT,
        log_file="logs/app.log"
    )

    logger.info(
        "User Service started",
        docs_url="http://127.0.0.1:8000/docs",
        redoc_url="http://127.0.0.1:8000/redoc",
        health_url="http://127.0.0.1:8000/health"
    )

    yield

    # Очистка при завершении
    logger.info("User Service shutdown")
