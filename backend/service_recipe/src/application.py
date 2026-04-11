"""
FastAPI application factory

Создаёт и настраивает FastAPI приложение
"""

from fastapi import FastAPI

from backend.service_recipe.src.lifespan import lifespan
from backend.service_recipe.src.infrastructure import container
from backend.shared.logging.config import setup_logging
from backend.shared.logging.middleware import LoggingMiddleware
from backend.service_recipe.src.api import api_router


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение
    """

    api_config = container.api_config()
    monitoring_config = container.monitoring_config()

    setup_logging(
        debug=monitoring_config.DEBUG,
        json_output=monitoring_config.LOG_FORMAT,
        log_file="logs/app.log"
    )

    app = FastAPI(
        title=api_config.API_TITLE,
        description=api_config.API_DESCRIPTION,
        version=api_config.API_VERSION,
        docs_url="/docs" if api_config.DEBUG else None,
        redoc_url="/redoc" if api_config.DEBUG else None,
        lifespan=lifespan
    )

    # Подключаем middleware логирования
    app.add_middleware(
        LoggingMiddleware,
        service_name="Recipe_Service"
    )

    # Подключаем API роутеры
    app.include_router(api_router)

    return app
