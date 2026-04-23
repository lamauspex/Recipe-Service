"""
Централизованное логирование для всех сервисов
"""


from backend.shared.logging.logger import get_logger, Logger
from backend.shared.logging.middleware import LoggingMiddleware

__all__ = [
    "get_logger",
    "Logger",
    "LoggingMiddleware"
]
