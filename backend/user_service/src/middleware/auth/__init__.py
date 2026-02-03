"""
Auth middleware - аутентификация и авторизация

"""

# JWT аутентификация
from .jwt import (
    JWTBearer,
    AdminBearer,
    get_current_active_user
)
# Основные FastAPI зависимости
from .dependencies import (
    get_current_user,
    get_current_admin_user
)
# Декораторы авторизации
from .decorators import (
    require_admin,
    require_active_user,
    require_role,
    require_permission
)
# Базовые функции
from .core import (
    is_admin,
    is_active,
    has_role
)

__all__ = [
    # JWT аутентификация
    "JWTBearer",
    "AdminBearer",
    "get_current_active_user",
    # Основные зависимости
    "get_current_user",
    "get_current_admin_user",
    # Декораторы
    "require_admin",
    "require_active_user",
    "require_role",
    "require_permission",
    # Базовые функции
    "is_admin",
    "is_active",
    "has_role"
]
