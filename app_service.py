

"""
Управление жизненным циклом приложения User Service
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.database_service.src import (
    get_connection_manager,
    get_migration_runner
)
from backend.user_service.src.api import api_router as api_router_users
from backend.user_service.src.container import container as user_con


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
    if os.environ.get("TESTING") == "1" or os.environ.get("USER_SERVICE_TESTING") == "1":
        return

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

    # Подключаем API роутеры
    app.include_router(api_router_users)

    return app


# Приложение по умолчанию
app_service = create_app()
