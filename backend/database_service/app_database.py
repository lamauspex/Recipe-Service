"""
Главный файл приложения Database Service
"""

from fastapi import FastAPI

from .src.lifespan import lifespan
from .api import api_router


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение для Database Service
    """
    app = FastAPI(
        title="Database Service API",
        description="Сервис управления базой данных",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    app.include_router(api_router)

    return app


# Приложение по умолчанию
app_database = create_app()
