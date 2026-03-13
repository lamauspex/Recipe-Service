"""
Управление жизненным циклом приложения User Service
"""

import os

from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.service_database.src import (
    get_connection_manager,
    get_migration_runner
)
from backend.shared.logging.config import setup_logging


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

    setup_logging(debug=True)
    print("User Service запущен")

    # Пропускаем инициализацию в тестах
    if os.environ.get("TESTING") == "1" or os.environ.get(
            "USER_SERVICE_TESTING") == "1":
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
    print("🚀 User Service запущен")
    print("   ├── http://127.0.0.1:8000/docs     (Swagger)")
    print("   ├── http://127.0.0.1:8000/redoc    (ReDoc)")
    print("   └── http://127.0.0.1:8000/health   (Health)")


async def shutdown_handler():
    """Обработчик завершения приложения"""
    print("User Service процесс завершён")
