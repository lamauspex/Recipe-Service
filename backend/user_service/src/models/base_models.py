"""
Базовый класс для всех моделей user-service
"""

from sqlalchemy.orm import DeclarativeBase, declared_attr

from backend.user_service.src.models.mixin import (
    UUIDPrimaryKeyMixin,
    StatusMixin,
    TimestampMixin
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей user-service"""

    pass


class BaseModel(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    StatusMixin
):
    """Базовая модель для user-service"""

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
