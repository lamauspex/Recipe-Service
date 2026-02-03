"""
Современная система исключений для User Service

Модульная архитектура:
- types.py: HTTP статусы и структуры данных
- base.py: базовые классы исключений
- handlers.py: обработчики ошибок
- decorators.py: декораторы и утилиты
- convenience.py: удобные функции для быстрого использования
"""

from .types import HTTPStatus
from .base import (
    AppException,
    HTTPException,
    NotFoundException,
    ValidationException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
    RateLimitException,
    UserException,
    AuthException,
    SecurityException,
)
from .handlers import (
    error_handler,
    handle_exceptions
)
from .decorators import (
    safe_execution,
    exception_handler
)
from .convenience import (
    not_found,
    validation_error,
    unauthorized
)
__all__ = [
    # Types
    "HTTPStatus",
    # Base exceptions
    "AppException",
    "HTTPException",
    "NotFoundException",
    "ValidationException",
    "UnauthorizedException",
    "ForbiddenException",
    "ConflictException",
    "RateLimitException",
    "UserException",
    "AuthException",
    "SecurityException",
    # Handlers
    "error_handler",
    "handle_exceptions",
    # Decorators and utilities
    "safe_execution",
    "exception_handler",
    # Convenience functions
    "not_found",
    "validation_error",
    "unauthorized"
]
