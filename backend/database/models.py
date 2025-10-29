"""
Базовые модели данных для всех микросервисов
Содержит общие компоненты: UUID, временные метки, базовые классы
"""

from sqlalchemy import String, DateTime, func, TypeDecorator
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    declared_attr,
    relationship
)
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


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей
    Автоматически генерирует имя таблицы из имени класса
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Генерирует имя таблицы из имени класса
        """
        # Преобразуем CamelCase в snake_case и добавляем 's'
        import re
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        return f"{name}s"


class TimestampMixin:
    """
    Миксин для добавления временных меток created_at и updated_at
    """

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
    """
    Миксин для добавления UUID первичного ключа
    """

    id: Mapped[UUIDType] = mapped_column(
        UUIDTypeDecorator(),
        default=uuid4,
        primary_key=True,
        index=True,
        comment='Уникальный идентификатор'
    )


class StatusMixin:
    """
    Миксин для добавления статуса активности
    """

    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment='Флаг активности записи'
    )


class BaseModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, StatusMixin):
    """
    Базовая модель со всеми общими полями:
    - UUID id (первичный ключ)
    - created_at (время создания)
    - updated_at (время обновления)
    - is_active (статус активности)

    Все модели должны наследоваться от этого класса
    """

    __abstract__ = True  # Это абстрактный класс, не создает таблицу

    def __repr__(self) -> str:
        """Базовое строковое представление"""
        return f"<{self.__class__.__name__}(id={self.id})>"


class UserMixin:
    """
    Миксин для связей с пользователем
    Добавляет user_id и связь с моделью User
    """

    user_id: Mapped[UUIDType] = mapped_column(
        UUIDTypeDecorator(),
        nullable=False,
        index=True,
        comment='ID пользователя'
    )

    @declared_attr
    def user(cls):
        """Связь с моделью пользователя"""
        # Импорт внутри метода для избежания циклических импортов
        return relationship("User", backref=f"{cls.__tablename__}")


# Утилитные классы для конкретных случаев

class SoftDeleteMixin:
    """
    Миксин для мягкого удаления (soft delete)
    """

    deleted_at: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment='Время удаления (мягкое удаление)'
    )

    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        comment='Флаг удаления'
    )


class OrderingMixin:
    """
    Миксин для добавления порядка сортировки
    """

    order_index: Mapped[int] = mapped_column(
        default=0,
        comment='Индекс для сортировки'
    )


class VersionMixin:
    """
    Миксин для контроля версий (оптимистичная блокировка)
    """

    version: Mapped[int] = mapped_column(
        default=1,
        comment='Версия записи для оптимистичной блокировки'
    )
