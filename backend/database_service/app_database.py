"""
Главный файл приложения Database Service
"""

from fastapi import FastAPI

from .src.container import container
from .src.lifespan import lifespan
from .api import api_router


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение для Database Service
    """

    # Получаем настройки из контейнера
    config = container.config

    app = FastAPI(
        title=config.API_TITLE,
        description=config.API_DESCRIPTION,
        version=config.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    app.include_router(api_router)

    return app


# Приложение по умолчанию
app_database = create_app()
