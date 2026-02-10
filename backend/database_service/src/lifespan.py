"""
Управление жизненным циклом приложения Database Service
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from ..connection import database


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

    if os.environ.get("TESTING") == "1":
        return

    if not database.test_connection():
        raise Exception("Не удалось подключиться к базе данных")

    database.init_db()


async def shutdown_handler():
    """Обработчик завершения приложения"""

    print("Database Service процесс завершён")
