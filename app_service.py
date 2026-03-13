

"""
Управление жизненным циклом приложения User Service
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.service_database.src import (
    get_connection_manager,
    get_migration_runner
)
from backend.service_user.src.middleware.exception_middleware import (
    ExceptionHandlerMiddleware)
from backend.shared.logging import setup_logging, LoggingMiddleware
from backend.service_user.src.api import api_router as api_router_users
from backend.service_user.src.container import container as user_con

# Настройка логирования ПЕРЕД созданием приложения
# Только если не в тестовом режиме
if os.environ.get("TESTING") != "1" and os.environ.get("USER_SERVICE_TESTING") != "1":
    # Подключаем конфигурацию мониторинга из .env
    monitoring_config = user_con.monitoring_config()
    print(f">>> LOG_FORMAT: '{monitoring_config.LOG_FORMAT}'")
    print(f">>> DEBUG: '{monitoring_config.DEBUG}'")
    setup_logging(
        debug=monitoring_config.DEBUG,
        json_output=(monitoring_config.LOG_FORMAT == "json")
    )

# Отключаем стандартные логи Uvicorn
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(logging.WARNING)

# Отключаем ВСЕ логи Uvicorn
for logger_name in [
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
    "uvicorn.asgi"
]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)


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

    # Пропускаем инициализацию в тестах
    if os.environ.get("TESTING") == "1" or os.environ.get(
            "USER_SERVICE_TESTING") == "1":
        return

    # Настройка логирования уже выполнена в начале файла

    # Получаем connection_manager и migration_runner из database_service
    connection_manager = get_connection_manager()
    migration_runner = get_migration_runner()

    # Проверяем подключение к базе данных
    if not connection_manager.test_connection():
        raise Exception("Не удалось подключиться к базе данных")

    # Применяем миграции
    migration_runner.upgrade("head")
    print("✅ Database initialized successfully")


async def shutdown_handler():
    """Обработчик завершения приложения"""

    print("User Service процесс завершён")


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение
    """

    # Получаем настройки из контейнера
    api_config = user_con.api_config()

    app = FastAPI(
        title=api_config.API_TITLE,
        description=api_config.API_DESCRIPTION,
        version=api_config.API_VERSION,
        docs_url="/docs" if api_config.DEBUG else None,
        redoc_url="/redoc" if api_config.DEBUG else None,
        lifespan=lifespan
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handler Middleware
    app.add_middleware(ExceptionHandlerMiddleware)

    # Подключаем API роутеры
    app.include_router(api_router_users)

    # Подключаем middleware логирования
    app.add_middleware(
        LoggingMiddleware,
        service_name="User_Service"
    )

    return app


# Приложение по умолчанию
app_service = create_app()
