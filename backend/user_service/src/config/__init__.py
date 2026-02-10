"""
Конфигурация для User Auth Service
"""


from .settings import settings
from .api import api_config
from .auth import auth_config
from .base import BaseConfig
from .cache import cache_config
from .monitoring import monitoring_config


__all__ = [
    "settings",
    "api_config",
    "auth_config",
    "BaseConfig",
    "cache_config",
    "monitoring_config"
]
