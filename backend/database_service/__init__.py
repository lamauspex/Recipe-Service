"""
Database пакет для user-service
Предоставляет единую точку входа для работы с базой данных
"""

from .base import DBBaseConfig
from .database import database_config

__all__ = [
    "DBBaseConfig",
    "database_config",
]
