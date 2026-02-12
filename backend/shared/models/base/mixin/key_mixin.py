""" Миксин """

from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID as UUIDType, uuid4

from backend.shared.models.decorator.type_decorator import UUIDTypeDecorator


class UUIDPrimaryKeyMixin:
    """Миксин для добавления UUID первичного ключа"""

    id: Mapped[UUIDType] = mapped_column(
        UUIDTypeDecorator(),
        default=uuid4,
        primary_key=True,
        index=True,
        comment='Уникальный идентификатор'
    )
