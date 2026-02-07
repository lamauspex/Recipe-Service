"""Factory functions для middleware"""

from typing import Dict, Any, Optional
from fastapi import FastAPI

from user_service.config import settings
from user_service.middleware.logging.http import HTTPLoggingMiddleware
from user_service.middleware.exceptions.handlers import (
    setup_exception_handlers
)
from .security.advanced import (
    AdvancedSecurityMiddleware,
    SimpleSecurityMiddleware
)


class MiddlewareFactory:
    """Factory class для создания middleware с конфигурацией"""

    @staticmethod
    def create_security_middleware(level: str = "advanced") -> type:
        """
        Создает security middleware в зависимости от уровня
        """
        if level == "advanced":
            return AdvancedSecurityMiddleware
        else:
            return SimpleSecurityMiddleware

    @staticmethod
    def create_logging_middleware() -> type:
        """Создает logging middleware"""

        return HTTPLoggingMiddleware

    @staticmethod
    def configure_middleware_for_app(
        app: FastAPI,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Полная настройка middleware для приложения на основе конфигурации
        """

        if config is None:
            config = MiddlewareFactory.get_default_config()

        # Настройка обработчиков исключений
        if config.get("enable_exception_handlers", True):
            setup_exception_handlers(app)

        # Настройка logging middleware
        if config.get("enable_logging", True):
            logging_middleware = MiddlewareFactory.create_logging_middleware()
            app.add_middleware(logging_middleware)

        # Настройка security middleware
        if config.get("enable_security", True):
            security_level = config.get("security_level", "advanced")
            security_middleware = MiddlewareFactory.create_security_middleware(
                security_level)
            app.add_middleware(security_middleware)

    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Получает конфигурацию middleware по умолчанию"""

        return {
            "enable_exception_handlers": True,
            "enable_logging": settings.monitoring.ENABLE_REQUEST_LOGGING,
            "enable_security": True,
            "enable_rate_limiting": True,
            "security_level": "advanced",
            "log_level": settings.monitoring.LOG_LEVEL,
            "skip_paths": settings.monitoring.SKIP_LOGGING_PATHS
        }

    @staticmethod
    def get_production_config() -> Dict[str, Any]:
        """Получает конфигурацию для production"""

        return {
            "enable_exception_handlers": True,
            "enable_logging": True,
            "enable_security": True,
            "enable_rate_limiting": True,
            "security_level": "advanced",
            "log_level": "INFO",
            "skip_paths": settings.SKIP_LOGGING_PATHS
        }

    @staticmethod
    def get_development_config() -> Dict[str, Any]:
        """Получает конфигурацию для development"""

        return {
            "enable_exception_handlers": True,
            "enable_logging": True,
            "enable_security": True,
            "enable_rate_limiting": False,  # Отключаем в dev
            "security_level": "simple",
            "log_level": "DEBUG",
            "skip_paths": settings.SKIP_LOGGING_PATHS
        }


# Convenience functions для быстрого использования
def setup_production_middleware(app: FastAPI) -> None:
    """Настройка middleware для production"""

    config = MiddlewareFactory.get_production_config()
    MiddlewareFactory.configure_middleware_for_app(app, config)


def setup_development_middleware(app: FastAPI) -> None:
    """Настройка middleware для development"""

    config = MiddlewareFactory.get_development_config()
    MiddlewareFactory.configure_middleware_for_app(app, config)


def setup_minimal_middleware(app: FastAPI) -> None:
    """Минимальная настройка middleware (только исключения)"""

    setup_exception_handlers(app)


def setup_exception_handlers_only(app: FastAPI) -> None:
    """Настроить только обработчики исключений"""

    setup_exception_handlers(app)
