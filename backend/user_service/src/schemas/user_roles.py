"""
Схемы ролей и разрешений
"""

from enum import Enum, IntFlag
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# === SIMPLE ROLE ENUM (для обратной совместимости) ===
class UserRole(str, Enum):
    """Простой Enum ролей для обратной совместимости"""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


# === PERMISSION ENUM (для API) ===
class Permission(IntFlag):
    """Разрешения системы (битовая маска)"""

    NONE = 0
    READ = 1           # Чтение данных
    WRITE = 2          # Создание/редактирование
    DELETE = 4         # Удаление
    MANAGE_USERS = 8   # Управление пользователями
    MANAGE_ROLES = 16  # Управление ролями
    VIEW_STATS = 32    # Просмотр статистики
    SYSTEM_CONFIG = 64  # Системные настройки
    BAN_USERS = 128    # Блокировка пользователей
    FULL_ACCESS = 255  # Полный доступ

    @classmethod
    def from_list(cls, permissions: List[str]) -> int:
        """Создать битовую маску из списка строк"""

        result = cls.NONE
        for perm_name in permissions:
            if hasattr(cls, perm_name):
                result |= getattr(cls, perm_name)
        return result

    @property
    def list(self) -> List[str]:
        """Получить список названий разрешений"""

        return [p.name for p in Permission if
                self.has(p) and p != Permission.NONE]

    def has(self, permission: "Permission") -> bool:
        """Проверить наличие конкретного разрешения"""

        return bool(self & permission)


# === ROLE SCHEMAS ===
class RoleCreate(BaseModel):
    """Схема создания роли"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Системное имя роли"
    )
    display_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Отображаемое имя"
    )
    permissions: List[str] = Field(
        ...,
        description="Список разрешений"
    )
    description: Optional[str] = Field(
        None,
        max_length=500
    )

    model_config = ConfigDict(from_attributes=True)


class RoleUpdate(BaseModel):
    """Схема обновления роли"""

    display_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100
    )
    permissions: Optional[List[str]] = Field(
        None,
        description="Список разрешений"
    )
    description: Optional[str] = Field(
        None,
        max_length=500
    )
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class RoleResponse(BaseModel):
    """Схема ответа роли"""
    id: UUID
    name: str
    display_name: str
    description: Optional[str]
    permissions: List[str]
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    user_count: int = Field(
        default=0,
        description="Количество пользователей"
    )

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj) -> "RoleResponse":
        """Создать из ORM объекта"""

        permissions_int = obj.permissions
        perm_obj = Permission(permissions_int)
        return cls(
            id=obj.id,
            name=obj.name,
            display_name=obj.display_name,
            description=obj.description,
            permissions=perm_obj.list,
            is_system=obj.is_system,
            is_active=obj.is_active,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            user_count=len(obj.users) if hasattr(obj, 'users') else 0
        )


class RoleAssign(BaseModel):
    """Схема назначения роли пользователю"""

    user_id: UUID
    role_name: str

    model_config = ConfigDict(from_attributes=True)


class RoleRemove(BaseModel):
    """Схема удаления роли у пользователя"""

    user_id: UUID
    role_name: str

    model_config = ConfigDict(from_attributes=True)


# === USER WITH ROLES ===
class UserWithRoles(BaseModel):
    """Пользователь с ролями"""

    id: UUID
    user_name: str
    email: str
    roles: List[RoleResponse]
    permissions: List[str]

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj) -> "UserWithRoles":
        """Создать из ORM объекта User"""

        return cls(
            id=obj.id,
            user_name=obj.user_name,
            email=obj.email,
            roles=[RoleResponse.from_orm(r) for r in obj.roles],
            permissions=Permission(obj.all_permissions).list
        )
