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
    api_config = container.api_config()

    app = FastAPI(
        title=api_config.API_TITLE,
        description=api_config.API_DESCRIPTION,
        version=api_config.API_VERSION,
        docs_url="/docs" if api_config.DEBUG else None,
        redoc_url="/redoc" if api_config.DEBUG else None,
        lifespan=lifespan
    )

    # Подключаем API роутеры
    app.include_router(api_router)

    return app


# Приложение по умолчанию
app_users = create_app()
