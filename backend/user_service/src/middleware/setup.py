"""
Централизованная настройка middleware

Единая точка входа: setup_middleware(app)
"""

from fastapi import FastAPI

from user_service.config import settings
from user_service.middleware.logging import setup_logging
from user_service.middleware.exceptions.handlers import (
    setup_exception_handlers
)
from user_service.middleware.factories import MiddlewareFactory


def setup_middleware(app: FastAPI, env: str = None) -> None:
    """
    Единая настройка всех middleware для приложения

    Args:
        app: FastAPI приложение
        env: Окружение (production, development, testing)
             Если не указано - берется из settings.api.ENVIRONMENT
    """
    if env is None:
        env = settings.api.ENVIRONMENT

    # 1. Настройка логирования (structlog + trace_id)
    setup_logging()

    # 2. Обработчики исключений (всегда нужны)
    setup_exception_handlers(app)

    # 3. Security middleware (CORS, rate limiting, security headers)
    security_level = "advanced" if env == "production" else "simple"
    security_middleware = MiddlewareFactory.create_security_middleware(
        security_level)
    app.add_middleware(security_middleware)

    # 4. HTTP logging middleware (логирует все запросы/ответы)
    if settings.monitoring.ENABLE_REQUEST_LOGGING:
        logging_middleware = MiddlewareFactory.create_logging_middleware()
        app.add_middleware(logging_middleware)
