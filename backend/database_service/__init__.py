"""
Database пакет для user-service
Предоставляет единую точку входа для работы с базой данных
"""

from .connection import database, create_engine_for_service


__all__ = [
    "database",
    "create_engine_for_service"
]
