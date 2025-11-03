"""
Базовый класс для всех моделей user-service
"""
from sqlalchemy import (
    String,
    DateTime,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy import TypeDecorator
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


class Base(DeclarativeBase):
    """Базовый класс для всех моделей user-service"""
    pass


class TimestampMixin:
    """Миксин для добавления временных меток"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment='Время создания записи'
    )

    updated_at: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment='Время последнего обновления'
    )


class UUIDPrimaryKeyMixin:
    """Миксин для добавления UUID первичного ключа"""
    id: Mapped[UUIDType] = mapped_column(
        UUIDTypeDecorator(),
        default=uuid4,
        primary_key=True,
        index=True,
        comment='Уникальный идентификатор'
    )


class StatusMixin:
    """Миксин для добавления статуса активности"""
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment='Флаг активности записи'
    )


class BaseModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, StatusMixin):
    """Базовая модель для user-service"""
    __abstract__ = True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
