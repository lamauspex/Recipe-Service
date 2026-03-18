"""
Миксины для преобразования DTO

Содержит:
- DTOConverterMixin: преобразование в словари для БД/API
- DTOSerializationMixin: сериализация в специфические форматы
"""

from .dto_converter import DTOConverterMixin
from .dto_serialization import DTOSerializationMixin

__all__ = [
    'DTOConverterMixin',
    'DTOSerializationMixin'
]
