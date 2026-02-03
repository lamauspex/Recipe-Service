"""
Middleware package

Единая точка входа: from user_service.middleware import setup_middleware
"""

from .exceptions.handlers import setup_exception_handlers
from .setup import setup_middleware
from .logging import (
    setup_logging,
    get_trace_id,
    set_trace_id,
    HTTPLogger,
    ExceptionLogger,
    BusinessEventLogger,
)
from .security import (
    CORSConfig,
    SecurityHeadersConfig,
    RateLimiter,
)
from .auth import (
    get_current_user,
    get_current_admin_user,
    require_permission,
    require_admin,
)

__all__ = [
    # Единая настройка
    "setup_middleware",
    # Логирование
    "setup_logging",
    "get_trace_id",
    "set_trace_id",
    "HTTPLogger",
    "ExceptionLogger",
    "BusinessEventLogger",
    # Исключения
    "setup_exception_handlers",
    # Безопасность
    "CORSConfig",
    "SecurityHeadersConfig",
    "RateLimiter",
    # Авторизация
    "get_current_user",
    "get_current_admin_user",
    "require_permission",
    "require_admin",
]
