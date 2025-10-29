"""
Модели данных для user-service
Использует общие базовые классы из backend.database.models
"""
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import typing as t

# Импортируем общие базовые классы
from backend.database.models import (
    BaseModel,
    UUIDTypeDecorator,
    UserMixin
)


class User(BaseModel):
    """Модель пользователя"""

    # Переопределяем имя таблицы (так как базовый класс генерирует 'users')
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
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
            f"username='{self.username}', "
            f"email='{self.email}'"
            f")>"
        )


class RefreshToken(BaseModel, UserMixin):
    """Модель refresh token для JWT аутентификации"""

    __tablename__ = "refresh_tokens"

    # Переопределяем ForeignKey для user_id
    user_id: Mapped[str] = mapped_column(
        UUIDTypeDecorator(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment='ID пользователя'
    )

    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment='Значение токена'
    )

    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment='Флаг отзыва токена'
    )

    expires_at: Mapped[t.Optional[str]] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment='Время истечения'
    )

    # Связь с пользователем
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"
