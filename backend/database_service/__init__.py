"""
Database пакет для user-service
Предоставляет единую точку входа для работы с базой данных
"""

from .base import DatabaseBaseConfig
from .database import database_config

__all__ = [
    "DatabaseBaseConfig",
    "database_config",
]
