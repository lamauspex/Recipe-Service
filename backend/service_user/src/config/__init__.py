"""
Конфигурация для User Auth Service
"""


from .config_api import ApiConfig
from .config_auth import AuthConfig
from .base import BaseConfig
from .config_cors import CORSConfig
from .config_grpc import GrpcConfig

__all__ = [
    "ApiConfig",
    "AuthConfig",
    "BaseConfig",
    "CORSConfig",
    "GrpcConfig"
]
