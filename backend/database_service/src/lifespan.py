"""
Lifespan для database_service
Управляет жизненным циклом приложения
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

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
    # Startup
    connection_manager = container.connection_manager()

    if not connection_manager.test_connection():
        raise RuntimeError("Не удалось подключиться к базе данных")

    # Авто-миграции
    if os.getenv("AUTO_MIGRATE", "false").lower() == "true":
        container.migration_runner().upgrade()

    yield

    # Shutdown
    connection_manager.close()
