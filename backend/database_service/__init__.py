"""
Database Service - Экспорт зависимостей для других сервисов
"""

from .src.container import container, db_dependency

__all__ = [
    "container",
    "db_dependency",
]
