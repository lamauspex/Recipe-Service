"""
Базовые классы исключений
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .types import HTTPStatus, ErrorContext


class AppException(Exception):
    """
    Базовое исключение приложения
    """

    def __init__(
        self,
        message: str,
        status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code: str = "APP_ERROR",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.context = ErrorContext(
            message=message,
            status_code=status_code,
            error_code=error_code,
            details=details or {},
            cause=cause
        )
        super().__init__(self.context.message)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API ответов"""

        return {
            "error": {
                "message": self.context.message,
                "code": self.context.error_code,
                "status_code": self.context.status_code,
                "details": self.context.details,
                "timestamp": self.context.timestamp
            }
        }

    def __str__(self) -> str:
        return self.context.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.context.message}', \
            code='{self.context.error_code}')"


# HTTP Exceptions - современные, типизированные исключения
class HTTPException(AppException):
    """Базовое HTTP исключение"""

    def __init__(
        self,
        message: str,
        status_code: HTTPStatus,
        error_code: str = "HTTP_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            status_code,
            error_code,
            details
        )


class NotFoundException(HTTPException):
    """404 Not Found"""

    def __init__(
        self,
        message: str = "Ресурс не найден",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            HTTPStatus.NOT_FOUND,
            "NOT_FOUND",
            details
        )


class ValidationException(HTTPException):
    """422 Validation Error"""

    def __init__(
        self,
        message: str = "Ошибка валидации",
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if field_errors:
            details = details or {}
            details["field_errors"] = field_errors

        super().__init__(
            message,
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            details
        )


class UnauthorizedException(HTTPException):
    """401 Unauthorized"""

    def __init__(
        self,
        message: str = "Неавторизованный доступ",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            HTTPStatus.UNAUTHORIZED,
            "UNAUTHORIZED",
            details
        )


class ForbiddenException(HTTPException):
    """403 Forbidden"""

    def __init__(
        self,
        message: str = "Доступ запрещен",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            HTTPStatus.FORBIDDEN,
            "FORBIDDEN",
            details
        )


class ConflictException(HTTPException):
    """409 Conflict"""

    def __init__(
        self,
        message: str = "Конфликт данных",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            HTTPStatus.CONFLICT,
            "CONFLICT",
            details
        )


class RateLimitException(HTTPException):
    """429 Too Many Requests"""

    def __init__(
        self,
        message: str = "Слишком много запросов",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if retry_after:
            details = details or {}
            details["retry_after"] = retry_after

        super().__init__(
            message,
            HTTPStatus.TOO_MANY_REQUESTS,
            "RATE_LIMITED",
            details
        )


# Domain Exceptions - бизнес-логика
class UserException(AppException):
    """Базовое исключение пользователя"""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            HTTPStatus.BAD_REQUEST,
            "USER_ERROR",
            details
        )


class AuthException(AppException):
    """Базовое исключение аутентификации"""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            HTTPStatus.UNAUTHORIZED,
            "AUTH_ERROR",
            details
        )


class SecurityException(AppException):
    """Базовое исключение безопасности"""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            HTTPStatus.FORBIDDEN,
            "SECURITY_ERROR",
            details
        )
