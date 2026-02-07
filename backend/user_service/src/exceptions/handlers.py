"""
Обработчики исключений

"""

from __future__ import annotations

from typing import Any, Dict, Type, Callable, Optional
import logging

from .types import HTTPStatus
from .base import AppException


class ErrorHandler:
    """
    Современный обработчик исключений

    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.handlers: Dict[Type[Exception], Callable] = {}

    def register_handler(
            self,
            exception_type: Type[Exception], handler: Callable):
        """Регистрация кастомного обработчика исключений"""

        self.handlers[exception_type] = handler

    def handle(self, exc: Exception) -> Dict[str, Any]:
        """ Обработка исключения """

        # Логирование исключения
        self.logger.error(f"Exception occurred: {type(exc).__name__}: {exc}")

        # Поиск кастомного обработчика
        for exc_type, handler in self.handlers.items():
            if isinstance(exc, exc_type):
                return handler(exc)

        # Стандартная обработка для AppException
        if isinstance(exc, AppException):
            return exc.to_dict()

        # Обработка неизвестных исключений
        return self._handle_unknown_exception(exc)

    def _handle_unknown_exception(self, exc: Exception) -> Dict[str, Any]:
        """Обработка неизвестных исключений"""

        return {
            "error": {
                "message": "Внутренняя ошибка сервера",
                "code": "INTERNAL_ERROR",
                "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                "details": {
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc)
                }
            }
        }


# Глобальный экземпляр обработчика
error_handler = ErrorHandler()


def handle_exceptions(handler: Optional[Callable] = None):
    """
    Декоратор для обработки исключений в функциях
    """

    def decorator(func):
        from functools import wraps

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                if handler:
                    return handler(exc)
                return error_handler.handle(exc)
        return wrapper

    return decorator if handler else decorator
