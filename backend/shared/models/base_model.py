"""
Базовые классы — независимый слой
"""
import re
from sqlalchemy.orm import DeclarativeBase, declared_attr

from backend.shared.models.base.mixin import (
    UUIDPrimaryKeyMixin,
    StatusMixin,
    TimestampMixin
)


def _pluralize_table_name(name: str) -> str:
    """Генерация корректного множественного числа для имени таблицы"""

    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    if re.search(r'(s|x|z|ch|sh)$', name):
        return name + 'es'
    if name.endswith('y') and len(name) > 1 and name[-2] not in 'aeiou':
        return name[:-1] + 'ies'
    return name + 's'


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class BaseModel(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    StatusMixin
):
    """Базовая модель с UUID, временем и статусом"""

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return _pluralize_table_name(cls.__name__.lower())

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
