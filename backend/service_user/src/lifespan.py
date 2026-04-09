"""
Управление жизненным циклом приложения User Service
"""

import os
import signal
import multiprocessing

from contextlib import asynccontextmanager
from fastapi import FastAPI
from alembic import command
from alembic.config import Config

from backend.shared.database import ConnectionManager, DataBaseConfig
from backend.service_user.src.infrastructure import container
from backend.shared.logging.config import setup_logging
from backend.shared.logging.logger import get_logger

# Глобальная ссылка на процесс для управления
_grpc_process = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Управление жизненным циклом приложения """

    global logger
    logger = get_logger(__name__).bind(
        layer="lifespan",
        service="user"
    )
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


def _run_grpc_in_process(port: int):
    """Обёртка для запуска в отдельном процессе"""
    from backend.service_user.src.infrastructure.grpc_process import main
    main(port)


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

    # === gRPC в отдельном процессе ===
    global _grpc_process
    print(">>> [startup_handler] Starting gRPC server in separate process...")

    grpc_port = 50051  # TODO: брать из конфига

    _grpc_process = multiprocessing.Process(
        target=_run_grpc_in_process,
        args=(grpc_port,),
        name="grpc-server"
    )
    _grpc_process.start()

    print(
        f">>> [startup_handler] gRPC process started, PID: {_grpc_process.pid}"
    )

    # Даём время процессу запуститься
    import time
    time.sleep(2)

    # Проверяем что процесс жив
    if _grpc_process.is_alive():
        print(">>> [startup_handler] gRPC process is alive")
    else:
        print(">>> [startup_handler] WARNING: gRPC process died!")

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
        docs_url="http://127.0.0.1:8000/docs",
        redoc_url="http://127.0.0.1:8000/redoc",
        health_url="http://127.0.0.1:8000/health"
    )


async def shutdown_handler():
    """Обработчик завершения приложения"""
    global _grpc_process
    logger = get_logger(__name__).bind(
        layer="lifespan",
        service="user"
    )

    print(">>> [shutdown_handler] Starting shutdown...")

    # Останавливаем gRPC процесс
    if _grpc_process and _grpc_process.is_alive():
        print(
            f">>> [shutdown_handler] Stopping gRPC process (PID: "
            f"{_grpc_process.pid})..."
        )
        _grpc_process.terminate()
        _grpc_process.join(timeout=5)

        if _grpc_process.is_alive():
            print(">>> [shutdown_handler] Force killing gRPC process...")
            _grpc_process.kill()
            _grpc_process.join()

        print(">>> [shutdown_handler] gRPC process stopped")

    print(">>> [shutdown_handler] Cleanup complete")
    logger.info("User Service процесс завершён")
