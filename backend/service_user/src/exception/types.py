

"""
Типы и структуры данных для системы исключений

- HTTP статусы
- Структуры данных для ошибок
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from enum import IntEnum
from datetime import datetime


class HTTPStatus(IntEnum):
    """
    HTTP статусы - современный enum вместо магических чисел
    """

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503
    LOCKED = 423
    TOO_MANY_REQUESTS = 429


@dataclass
class ErrorContext:
    """
    Структурированный контекст ошибки
    """

    message: str
    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code: str = "APP_ERROR"
    details: Optional[Dict[str, Any]] = field(default_factory=dict)
    cause: Optional[Exception] = None
    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self):
        """
        Автоматическая установка времени
        """

        if self.timestamp == "auto":
            self.timestamp = datetime.utcnow().isoformat()
