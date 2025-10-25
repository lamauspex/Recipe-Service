"""
Модели данных для user-service
"""
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Text,
    func,
    TypeDecorator,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from uuid import UUID as UUIDType, uuid4
import typing as t
from datetime import datetime


class UUIDTypeDecorator(TypeDecorator):
    """
    Декоратор типа для совместимости UUID между SQLite и PostgreSQL
    В SQLite хранит как строку, в PostgreSQL как нативный UUID
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            return UUIDType(value)


# Создаем базовый класс для моделей
class Base(DeclarativeBase):
    pass


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id: Mapped[UUIDType] = mapped_column(
        UUIDTypeDecorator(),
        default=uuid4,
        primary_key=True,
        index=True,
        comment='Уникальный идентификатор'
    )
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
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment='Флаг активности'
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment='Флаг администратора'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment='Время создания'
    )
    updated_at: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment='Время обновления'
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


class RefreshToken(Base):
    """Модель refresh token для JWT аутентификации"""
    __tablename__ = "refresh_tokens"

    id: Mapped[UUIDType] = mapped_column(
        UUIDTypeDecorator(),
        default=uuid4,
        primary_key=True,
        index=True,
        comment='Уникальный идентификатор токена'
    )
    user_id: Mapped[UUIDType] = mapped_column(
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment='Время создания'
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment='Время истечения'
    )

    # Связь с пользователем
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"
