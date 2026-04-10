"""
Главный файл приложения User Service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.service_user.src.api import api_router
from backend.service_user.src.infrastructure.container import container
from backend.service_user.src.lifespan import lifespan
from backend.shared.logging.logger import get_logger
from backend.shared.logging.middleware import LoggingMiddleware
from backend.service_user.src.middleware.exception_middleware import (
    ExceptionHandlerMiddleware)


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение
    """
    logger = get_logger(__name__).bind(
        layer="lifespan",
        service="user"
    )

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
    logger.info(">>> FastAPI создан")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.CORS_ORIGINS,
        allow_credentials=cors_config.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(">>> CORS настроен")

    # Подключаем middleware логирования
    app.add_middleware(
        LoggingMiddleware,
        service_name="User_Service"
    )
    logger.info(">>> Middleware логирования настроен")

    # Exception Handler Middleware
    app.add_middleware(ExceptionHandlerMiddleware)
    logger.info(">>> Middleware обработки исключений настроен")

    # Подключаем API роутеры
    app.include_router(api_router)
    logger.info(">>> API роутеры подключены")

    return app
