"""
Централизованное логирование

Объединяет HTTP, Exception и Business логирование в единую систему.
Использует structlog с конфигурацией из config.py.

Пример использования:
    from user_service.middleware.logging import (
        setup_logging,
        HTTPLogger,
        ExceptionLogger,
        BusinessEventLogger,
        get_trace_id,
        set_trace_id,
        trace_id_var,
    )
"""

from __future__ import annotations

from user_service.middleware.logging.utils_trace_id import (
    get_trace_id,
    set_trace_id,
    clear_trace_id,
    trace_id_var,
)

# Конфигурация
from user_service.middleware.logging.config import (
    setup_logging,
    get_log_level_from_config,
)

# Logger классы
from user_service.middleware.logging.http import (
    HTTPLogger,
    HTTPLoggingMiddleware,
)

from user_service.middleware.logging.exception import ExceptionLogger

from user_service.middleware.logging.business import BusinessEventLogger

from user_service.middleware.logging.loggers import (
    http_logger,
    exception_logger,
    business_logger,
    security_logger,
)


__all__ = [
    # Конфигурация
    "setup_logging",
    "get_log_level_from_config",
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
