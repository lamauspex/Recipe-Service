"""
Базовые исключения для сервисного слоя
"""
from typing import Dict, Optional, Any
from enum import Enum


class ErrorCode(Enum):
    """Коды ошибок для единообразной обработки"""

    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    ACCESS_DENIED = "ACCESS_DENIED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class ServiceException(Exception):
    """Базовое исключение для сервисного слоя"""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(f"{error_code.value}: {message}")


class ValidationException(ServiceException):
    """Исключение для ошибок валидации"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            ErrorCode.VALIDATION_ERROR,
            message,
            details,
            status_code=400
        )


class NotFoundException(ServiceException):
    """Исключение для случаев, когда ресурс не найден"""

    def __init__(self, message: str, resource: str = "Resource"):
        super().__init__(
            ErrorCode.USER_NOT_FOUND,
            f"{resource} not found: {message}",
            status_code=404
        )


class ConflictException(ServiceException):
    """Исключение для конфликтов (например, пользователь уже существует)"""

    def __init__(self, message: str):
        super().__init__(
            ErrorCode.USER_ALREADY_EXISTS,
            message,
            status_code=409
        )


class UnauthorizedException(ServiceException):
    """Исключение для ошибок авторизации"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            ErrorCode.INVALID_CREDENTIALS,
            message,
            status_code=401
        )


class ForbiddenException(ServiceException):
    """Исключение для ошибок доступа"""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            ErrorCode.ACCESS_DENIED,
            message,
            status_code=403
        )
