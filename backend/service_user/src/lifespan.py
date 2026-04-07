"""
Управление жизненным циклом приложения User Service
"""

import os
import signal

from contextlib import asynccontextmanager
from fastapi import FastAPI
from alembic import command
from alembic.config import Config

from backend.shared.database import ConnectionManager, DataBaseConfig
from backend.service_user.src.infrastructure import (
    container, serve_grpc)
from backend.shared.logging.config import setup_logging
from backend.shared.logging.logger import get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Управление жизненным циклом приложения """

    global logger
    logger = get_logger(__name__).bind(layer="lifespan", service="user")
    print(">>> logger настроен")

    # Запускаем миграции при старте
    alembic_cfg = Config("backend/service_user/migration/alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print(">>> Миграции выполнены")

    # Код запуска
    await startup_handler()
    print(">>> Запущен")

    yield

    # Код завершения
    await shutdown_handler()


def handle_shutdown(signum, frame):
    """Обработчик сигнала завершения"""
    exit(0)


async def startup_handler():
    """ Обработчик запуска приложения """
    print(">>> [startup_handler] START")
    global logger

    config = DataBaseConfig()
    connection_manager = ConnectionManager(config)
    print(">>> [startup_handler] DB config created")

    logger = get_logger(__name__).bind(
        layer="lifespan",
        service="user"
    )

    print(">>> [startup_handler] Creating gRPC server...")
    grpc_server = await serve_grpc(50051)
    print(">>> [startup_handler] gRPC server created")
    await grpc_server.start()
    print(">>> [startup_handler] gRPC server started")

    # Регистрируем обработчик сигналов
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    monitoring_config = container.monitoring_config()
    setup_logging(
        debug=monitoring_config.DEBUG,
        json_output=monitoring_config.LOG_FORMAT,
        log_file="logs/app.log"
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
        "User Service started",
        docs_url="http://127.0.0.1:8001/docs",
        redoc_url="http://127.0.0.1:8001/redoc",
        health_url="http://127.0.0.1:8001/health"
    )


async def shutdown_handler():
    """Обработчик завершения приложения"""
    logger = get_logger(__name__).bind(
        layer="lifespan",
        service="user"
    )
    logger.info("User Service процесс завершён")
