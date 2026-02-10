"""
Главный файл приложения User Service
"""

from fastapi import FastAPI

from backend.user_service.src.api import api_router
from backend.user_service.src.container import container
from backend.user_service.src.lifespan import lifespan


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение
    """

    # Получаем настройки из контейнера
    config = container.config

    app = FastAPI(
        title=config.api.API_TITLE,
        description=config.api.API_DESCRIPTION,
        version=config.api.API_VERSION,
        docs_url="/docs" if config.monitoring.DEBUG else None,
        redoc_url="/redoc" if config.monitoring.DEBUG else None,
        lifespan=lifespan
    )

    # Подключаем API роутеры
    app.include_router(api_router)


# Приложение по умолчанию
app_users = create_app()
