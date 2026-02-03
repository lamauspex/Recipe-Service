"""
Centralized Logging System for user_service

Объединяет HTTP, Exception и Business логирование в единую систему.
Использует structlog с поддержкой trace_id для трейсинга.

"""

from .logging import (
    setup_logging,
    get_trace_id,
    set_trace_id,
    clear_trace_id,
    trace_id_var,
    HTTPLogger,
    ExceptionLogger,
    BusinessEventLogger,
    HTTPLoggingMiddleware,
    http_logger,
    exception_logger,
    business_logger,
    security_logger,
)

__all__ = [
    # Конфигурация
    "setup_logging",
    # Trace ID
    "get_trace_id",
    "set_trace_id",
    "clear_trace_id",
    "trace_id_var",
    # Logger классы
    "HTTPLogger",
    "ExceptionLogger",
    "BusinessEventLogger",
    "HTTPLoggingMiddleware",
    # Loggers
    "http_logger",
    "exception_logger",
    "business_logger",
    "security_logger",
]
