"""
Database пакет
=====================
Предоставляет единую точку входа для работы с базой данных
и DI контейнером для управления зависимостями

"""

from .base import DBBaseConfig
from .database import DataBaseConfig
from .connection import DatabaseManager
from .container import container, Container
from .providers import (
    database_providers,
    get_db_session,
    get_db_context,
    get_db_dependency,
    get_database_config
)

__all__ = [
    # Базовые компоненты
    "DBBaseConfig",
    "DataBaseConfig",

    # Менеджеры
    "DatabaseManager",

    # DI контейнер
    "Container",
    "container",

    # Провайдеры зависимостей
    "database_providers",
    "get_db_session",
    "get_db_context",
    "get_db_dependency",
    "get_database_config",
]
