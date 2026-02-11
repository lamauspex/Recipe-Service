
from .src.config.base import DBBaseConfig
from .src.config.database import DataBaseConfig
from .src.connection import DatabaseManager
from .src.container import container, Container
from .src.providers import (
    database_providers,
    get_db_session,
    get_db_context,
    get_db_dependency,
    get_database_config
)
from backend.shared.models import (
    Base,
    BaseModel,
    User,
    RoleModel,
    Permission,
    RefreshToken,
    LoginAttempt
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

    # Модели данных
    "Base",
    "BaseModel",
    "User",
    "RoleModel",
    "Permission",
    "RefreshToken",
    "LoginAttempt",
]
