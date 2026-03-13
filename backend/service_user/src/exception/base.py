""" Базовые исключения """

from typing import Any, Dict, Optional


class AppException(Exception):
    """Базовое исключение приложения"""

    def __init__(
        self,
        message: str,
        status_code: int,
        code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для ответа"""
        return {
            "error": {
                "message": self.message,
                "code": self.code,
                "status_code": self.status_code,
                "details": self.details
            }
        }


class ConflictException(AppException):
    """409 - Конфликт (уже существует)"""

    def __init__(
        self,
        message: str = "Конфликт",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=409,
            code="CONFLICT",
            details=details
        )


class NotFoundException(AppException):
    """404 - Не найдено"""

    def __init__(
        self,
        message: str = "Ресурс не найден",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=404,
            code="NOT_FOUND",
            details=details
        )


class ValidationException(AppException):
    """422 - Ошибка валидации"""

    def __init__(
        self,
        message: str = "Ошибка валидации",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=422,
            code="VALIDATION_ERROR",
            details=details
        )
