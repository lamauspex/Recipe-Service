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


from backend.shared.models.base_model import BaseModel
from backend.shared.models.enums import ROLES, Permission, Role


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

    last_login: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment='Последний вход в систему'
    )

    login_count: Mapped[int] = mapped_column(
        default=0,
        comment='Количество входов в систему'
    )

    role_name: Mapped[str] = mapped_column(
        String(50),
        default="user",
        nullable=False,
        index=True,
        comment='Роль пользователя'
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

    @property
    def role(self) -> Role:
        """Получить объект роли"""
        return ROLES[self.role_name]

    @property
    def permissions(self) -> Permission:
        """Получить разрешения пользователя"""
        return self.role.permissions
