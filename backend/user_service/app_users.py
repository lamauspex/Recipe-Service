"""
Главный файл приложения User Service
"""


from fastapi import FastAPI

from backend.user_service.src.api import api_router
from backend.user_service.src.config import settings
from backend.user_service.src.middleware import setup_middleware
from backend.user_service.lifespan import lifespan


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение

    """

    app = FastAPI(
        title=settings.api.API_TITLE,
        description=settings.api.API_DESCRIPTION,
        version=settings.api.API_VERSION,
        docs_url="/docs" if settings.database.DEBUG else None,
        redoc_url="/redoc" if settings.database.DEBUG else None,
        lifespan=lifespan
    )

    # Настройка middleware по окружению
    setup_middleware(app)

    # Подключаем API роутеры
    app.include_router(api_router)

    return app


# Приложение по умолчанию
app_users = create_app()
