"""
Модели данных для user-service
"""

import typing as t
from datetime import datetime
from sqlalchemy import (
    String,
    Boolean,
    Text,
    DateTime
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from backend.database_service.src.models.base_models import BaseModel
from backend.database_service.src.models.role_model import Permission, RoleModel


class User(BaseModel):
    """Модель пользователя"""

    user_name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment='Имя пользователя'
    )

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        comment='Email пользователя'
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment='Хешированный пароль'
    )

    full_name: Mapped[t.Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment='Полное имя'
    )

    bio: Mapped[t.Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='Биография пользователя'
    )

    # Поля для email верификации
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment='Подтвержден ли email'
    )

    verification_token: Mapped[t.Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment='Токен для подтверждения email'
    )

    verification_expires_at: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment='Время истечения токена верификации'
    )

    # Поля для сброса пароля
    password_reset_token: Mapped[t.Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment='Токен для сброса пароля'
    )

    password_reset_expires_at: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment='Время истечения токена сброса пароля'
    )

    # Связь с refresh токенами
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Связь с попытками входа
    login_attempts = relationship(
        "LoginAttempt",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Связь с ролями (M:N через user_roles table)
    roles: Mapped[t.List["RoleModel"]] = relationship(
        "RoleModel",
        secondary="user_roles",  # Ссылка на таблицу user_roles
        back_populates="users",
        lazy="selectin",
        doc="Роли пользователя"
    )

    last_login: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment='Последний вход в систему'
    )

    login_count: Mapped[int] = mapped_column(
        default=0,
        comment='Количество входов в систему'
    )

    # === CONVENIENCE METHODS ===
    @property
    def primary_role(self) -> t.Optional["RoleModel"]:
        """Получить первую роль (для обратной совместимости)"""

        return self.roles[0] if self.roles else None

    @property
    def all_permissions(self) -> int:
        """Получить объединённые разрешения всех ролей"""

        result = Permission.NONE
        for role in self.roles:
            result |= role.permissions
        return result

    def has_permission(self, permission: int) -> bool:
        """Проверка разрешения (учитывая все роли)"""

        return bool(self.all_permissions & permission)

    def has_role(self, role_name: str) -> bool:
        """Проверка наличия конкретной роли"""

        return any(r.name == role_name for r in self.roles)

    def add_role(self, role: "RoleModel") -> None:
        """Добавить роль"""
        if self.roles is None:
            self.roles = []
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role: "RoleModel") -> None:
        """Убрать роль"""

        if role in self.roles:
            self.roles.remove(role)
