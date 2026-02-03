"""
Функции для быстрого создания исключений
"""

from __future__ import annotations

from typing import Dict, Optional

from .base import (
    NotFoundException,
    ValidationException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
    RateLimitException,
)


class ServiceException(Exception):
    """ Базовое исключение для ошибок бизнес-логики сервиса """

    def __init__(self, message: str):
        super().__init__(message)


def not_found(
    message: str = "Ресурс не найден",
    **kwargs
) -> NotFoundException:
    """
    Функция для создания NotFoundException
    """

    return NotFoundException(message, kwargs)


def validation_error(
    message: str = "Ошибка валидации",
    field_errors: Optional[Dict[str, str]] = None,
    **kwargs
) -> ValidationException:
    """
    Функция для создания ValidationException
    """

    return ValidationException(message, field_errors, kwargs)


def unauthorized(
    message: str = "Неавторизованный доступ",
    **kwargs
) -> UnauthorizedException:
    """ Функция для создания UnauthorizedException """

    return UnauthorizedException(message, kwargs)


def forbidden(
    message: str = "Доступ запрещен",
    **kwargs
) -> ForbiddenException:
    """ Функция для создания ForbiddenException """

    return ForbiddenException(message, kwargs)


def conflict(
    message: str = "Конфликт данных",
    **kwargs
) -> ConflictException:
    """Функция для создания ConflictException"""

    return ConflictException(message, kwargs)


def rate_limited(
    message: str = "Слишком много запросов",
    **kwargs
) -> RateLimitException:
    """Функция для создания RateLimitException"""

    return RateLimitException(message, kwargs)
