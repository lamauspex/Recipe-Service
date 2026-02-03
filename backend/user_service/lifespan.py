
"""
Управление жизненным циклом приложения
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.database_service.connection import database
from backend.user_service.src.services import RoleService


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

    if not database.test_connection():
        raise Exception("Не удалось подключиться к базе данных")

    database.init_db()
    session = database.get_db_session()
    try:
        RoleService(session).ensure_default_roles()
    finally:
        session.close()


async def shutdown_handler():
    """Обработчик завершения приложения"""

    print("Процесс завершён")
