
"""
Базовые классы исключений
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .types import ErrorContext, HTTPStatus


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
