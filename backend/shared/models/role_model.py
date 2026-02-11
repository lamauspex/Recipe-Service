"""
Модель ролей и разрешений для RBAC
Продакшен-стандарт: роли и permissions в БД
"""

import typing as t
from enum import IntFlag
from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    Table,
    Column,
    Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.models.base_models import BaseModel
from backend.shared.models.decorator import UUIDTypeDecorator
from backend.shared.models.user_models import User


# === PERMISSIONS SYSTEM ===
class Permission(IntFlag):
    """Разрешения системы (битовая маска)"""

    NONE = 0
    READ = 1          # Чтение данных
    WRITE = 2         # Создание/редактирование
    DELETE = 4        # Удаление
    MANAGE_USERS = 8  # Управление пользователями
    MANAGE_ROLES = 16  # Управление ролями
    VIEW_STATS = 32   # Просмотр статистики
    SYSTEM_CONFIG = 64  # Системные настройки
    BAN_USERS = 128   # Блокировка пользователей
    FULL_ACCESS = 255  # Полный доступ


# === ASSOCIATION TABLE ===
user_roles = Table(
    "user_roles",
    BaseModel.metadata,
    Column(
        "user_id",
        UUIDTypeDecorator(),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "role_id",
        UUIDTypeDecorator(),
        ForeignKey("rolemodel.id", ondelete="CASCADE"),
        primary_key=True
    ),
)


# === ROLE MODEL ===
class RoleModel(BaseModel):
    """
    Модель роли.
    Все роли (включая admin, user, moderator) хранятся в БД.
    """

    __tablename__ = "rolemodel"

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment='Системное имя роли (admin, user, moderator)'
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment='Отображаемое имя (Администратор, Пользователь...)'
    )

    description: Mapped[t.Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='Описание роли'
    )

    permissions: Mapped[int] = mapped_column(
        Integer,
        default=Permission.NONE,
        comment='Битовая маска разрешений'
    )

    is_system: Mapped[bool] = mapped_column(
        default=False,
        comment='Системная роль (нельзя удалить)'
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment='Активна ли роль'
    )

    users: Mapped[t.List["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin",
        viewonly=True
    )

    @property
    def permissions_list(self) -> list[Permission]:
        """Получить список разрешений"""

        return [p for p in Permission if p != Permission.NONE
                and self.permissions & p]

    def has_permission(self, permission: Permission) -> bool:
        """Проверка конкретного разрешения"""

        return bool(self.permissions & permission)

    def add_permission(self, permission: Permission) -> None:
        """Добавить разрешение"""

        self.permissions |= permission

    def remove_permission(self, permission: Permission) -> None:
        """Убрать разрешение"""

        self.permissions &= ~permission

    def __repr__(self) -> str:
        return f"<Role(name='{self.name}', permissions={self.permissions})>"


# === DEFAULT ROLES ===
DEFAULT_ROLES = {
    "user": {
        "display_name": "Пользователь",
        "description": "Базовые права доступа",
        "permissions": Permission.READ,
        "is_system": True,
    },
    "moderator": {
        "display_name": "Модератор",
        "description": "Права на модерацию контента",
        "permissions": Permission.READ |
        Permission.WRITE | Permission.VIEW_STATS,
        "is_system": True,
    },
    "admin": {
        "display_name": "Администратор",
        "description": "Полный доступ к системе",
        "permissions": Permission.FULL_ACCESS,
        "is_system": True,
    },
}
