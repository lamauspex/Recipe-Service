"""
Базовый класс для всех моделей user-service
"""

import re
from sqlalchemy.orm import DeclarativeBase, declared_attr

from backend.shared.models.base.mixin import (
    UUIDPrimaryKeyMixin,
    StatusMixin,
    TimestampMixin
)


def _pluralize_table_name(name: str) -> str:
    """
    Генерация корректного множественного числа для имени таблицы

    Правила:
    - Если имя уже заканчивается на 's', 'x', 'z', 'ch', 'sh' → добавляем 'es'
    - Если заканчивается на 'y' и предпоследняя буква не гласная → 'y' → 'ies'
    - Иначе → добавляем 's'
    """
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    # Слова, оканчивающиеся на s, x, z, ch, sh
    if re.search(r'(s|x|z|ch|sh)$', name):
        return name + 'es'
    # Слова, оканчивающиеся на y (после согласной)
    if name.endswith('y') and len(name) > 1 and name[-2] not in 'aeiou':
        return name[:-1] + 'ies'
    # По умолчанию добавляем 's'
    return name + 's'


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
        return _pluralize_table_name(cls.__name__.lower())

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
