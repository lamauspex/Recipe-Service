"""
Главный файл приложения User Service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.service_user.src.api import api_router
from backend.service_user.src.infrastructure.container import container
from backend.service_user.src.lifespan import lifespan
from backend.shared.logging.middleware import LoggingMiddleware
from backend.service_user.src.middleware.exception_middleware import (
    ExceptionHandlerMiddleware)


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение
    """

    # Получаем настройки из контейнера
    api_config = container.api_config()
    cors_config = container.cors_config()

    app = FastAPI(
        title=api_config.API_TITLE,
        description=api_config.API_DESCRIPTION,
        version=api_config.API_VERSION,
        docs_url="/docs" if api_config.DEBUG else None,
        redoc_url="/redoc" if api_config.DEBUG else None,
        lifespan=lifespan
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.CORS_ORIGINS,
        allow_credentials=cors_config.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключаем middleware логирования
    app.add_middleware(
        LoggingMiddleware,
        service_name="User_Service"
    )

    # Exception Handler Middleware
    app.add_middleware(ExceptionHandlerMiddleware)

    # Подключаем API роутеры
    app.include_router(api_router)

    return app
