"""
Управление жизненным циклом приложения User Service
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.service_database.src import (
    get_connection_manager,
    get_migration_runner)


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

    if os.environ.get("USER_SERVICE_TESTING") == "1":
        return

    # Получаем connection_manager
    connection_manager = get_connection_manager()

    # Проверяем подключение
    if not connection_manager.test_connection():
        raise Exception("Не удалось подключиться к базе данных")

    # Применяем миграции
    migration_runner = get_migration_runner()
    migration_runner.upgrade("head")
    print("✅ Database initialized successfully")


async def shutdown_handler():
    """Обработчик завершения приложения"""

    print("User Service процесс завершён")
