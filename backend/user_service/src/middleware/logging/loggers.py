"""
Bound loggers для разных типов событий

Единый источник истинности для всех логгеров приложения.
Используется для предотвращения дублирования и несогласованности.
"""

from __future__ import annotations

import structlog


# Bound loggers для разных типов событий
# Каждый логгер — для своей предметной области
http_logger = structlog.get_logger("http_requests")
exception_logger = structlog.get_logger("exceptions")
business_logger = structlog.get_logger("business_events")
security_logger = structlog.get_logger("security")


__all__ = [
    "http_logger",
    "exception_logger",
    "business_logger",
    "security_logger",
]
