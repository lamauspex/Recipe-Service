"""
Схемы Pydantic для user-service
Удобный импорт всех схем через один файл
"""

# Базовые схемы пользователей
from .schemas import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse
)
# Схемы для работы с токенами
from .token_schems import (
    Token,
    TokenData,
    RefreshTokenRequest
)
# Схемы для работы с паролями
from .password_schemas import (
    UserLogin,
    PasswordResetRequest,
    PasswordResetConfirm
)
# Схемы для администрирования
from .admin_schemas import (
    AdminUserResponse,
    AdminActionRequest,
    RoleUpdateRequest,
    AdminStatsResponse
)
# Роли и разрешения
from .user_roles import (
    UserRole,
    Permission,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleAssign,
    RoleRemove,
    UserWithRoles,
)
# Экспорт всех схем для удобного импорта
__all__ = [
    # Базовые схемы
    'UserBase',
    'UserCreate',
    'UserUpdate',
    'UserResponse',
    # Токены
    'Token',
    'TokenData',
    'RefreshTokenRequest',
    # Пароли
    'UserLogin',
    'PasswordResetRequest',
    'PasswordResetConfirm',
    # Администрирование
    'AdminUserResponse',
    'AdminActionRequest',
    'RoleUpdateRequest',
    'AdminStatsResponse',
    # Роли и разрешения
    'UserRole',
    'Permission',
    'RoleCreate',
    'RoleUpdate',
    'RoleResponse',
    'RoleAssign',
    'RoleRemove',
    'UserWithRoles',
]
