"""
Модели данных для user-service
Автономная реализация без зависимостей от общих модулей
"""

import typing as t
from sqlalchemy import (
    String,
    Boolean,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.services.user_service.models.base_models import BaseModel


class User(BaseModel):
    """Модель пользователя"""
    __tablename__ = "users"

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

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment='Флаг администратора'
    )

    # Связь с refresh токенами
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<User("
            f"id={self.id}, "
            f"user_name='{self.user_name}', "
            f"email='{self.email}'"
            f")>"
        )
