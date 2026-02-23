"""
Централизованное логирование для всех сервисов
"""

from backend.shared.logging.config import setup_logging
from backend.shared.logging.logger import get_logger, Logger
from backend.shared.logging.middleware import LoggingMiddleware
from backend.shared.logging.service_logger import ServiceLogger

__all__ = [
    "setup_logging",
    "get_logger",
    "Logger",
    "LoggingMiddleware",
    "ServiceLogger",
]
