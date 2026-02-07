"""
Логирование исключений приложения
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from user_service.config import settings
from user_service.exceptions.base import AppException
from user_service.middleware.logging.utils_trace_id import get_trace_id
from user_service.middleware.logging.loggers import exception_logger


class ExceptionLogger:
    """
    Централизованный логировщик исключений

    Соответствует принципу единственной ответственности (SRP):
    - Только логирование исключений
    """

    @staticmethod
    def log_exception(
        exception: Exception,
        context: Optional[dict[str, Any]] = None,
        level: str = "ERROR",
        trace_id: Optional[str] = None
    ) -> str:
        """
        Логирование исключения

        Args:
            exception: Исключение для логирования
            context: Дополнительный контекст
            level: Уровень логирования
            trace_id: Trace ID (берётся из контекста если не передан)

        Returns:
            str: Уникальный идентификатор ошибки
        """
        # Проверяем, включено ли логирование исключений
        if not settings.monitoring.ENABLE_EXCEPTION_LOGGING:
            return str(uuid.uuid4())[:12]

        error_id = str(uuid.uuid4())[:12]
        timestamp = datetime.utcnow().isoformat()

        log_data = {
            "error_id": error_id,
            "trace_id": trace_id or get_trace_id(),
            "timestamp": timestamp,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "context": context or {},
        }

        # Добавляем traceback только для отладки
        import traceback as tb
        log_data["traceback"] = tb.format_exc()

        log_method = getattr(
            exception_logger, level.lower(), exception_logger.error)
        log_method("exception", **log_data)

        return error_id

    @staticmethod
    def log_app_exception(
        exception: AppException,
        context: Optional[dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """
        Логирование кастомного AppException

        Args:
            exception: AppException для логирования
            context: Дополнительный контекст
            trace_id: Trace ID (берётся из контекста если не передан)

        Returns:
            str: Уникальный идентификатор ошибки
        """
        # Проверяем, включено ли логирование исключений
        if not settings.monitoring.ENABLE_EXCEPTION_LOGGING:
            return str(uuid.uuid4())[:12]

        error_id = str(uuid.uuid4())[:12]
        timestamp = datetime.utcnow().isoformat()

        log_data = {
            "error_id": error_id,
            "trace_id": trace_id or get_trace_id(),
            "timestamp": timestamp,
            "error_code": exception.context.error_code,
            "status_code": exception.context.status_code,
            "exception_type": type(exception).__name__,
            "exception_message": exception.context.message,
            "details": exception.context.details,
            "context": context or {},
        }

        exception_logger.error("app_exception", **log_data)
        return error_id
