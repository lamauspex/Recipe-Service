"""
Конфигурация для User Auth Service
"""


from .config_api import ApiConfig
from .config_auth import AuthConfig
from .base import BaseConfig
from .config_cache import CacheConfig
from .config_monitoring import MonitoringConfig


__all__ = [
    "settings",
    "ApiConfig",
    "AuthConfig",
    "BaseConfig",
    "CacheConfig",
    "MonitoringConfig"
]
