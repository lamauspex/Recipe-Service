"""
FastAPI application factory

Создаёт и настраивает FastAPI приложение
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.service_recipe.src.lifespan import lifespan
from backend.service_recipe.src.infrastructure import container
from backend.shared.logging.middleware import LoggingMiddleware
from backend.service_recipe.src.middleware.request_logger import RequestLoggingMiddleware
from backend.service_recipe.src.api import api_router


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение
    """

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

    # CORS ПЕРВЫЙ
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.CORS_ORIGINS,
        allow_credentials=cors_config.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request Logging Middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Подключаем middleware логирования
    app.add_middleware(
        LoggingMiddleware,
        service_name="Recipe_Service"
    )

    # Подключаем API роутеры
    app.include_router(api_router)

    return app
