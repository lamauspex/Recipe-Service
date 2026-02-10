from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID as UUIDType, uuid4

from backend.user_service.duble_service_dtoschemas.models.decorator import UUIDTypeDecorator


class UUIDPrimaryKeyMixin:
    """Миксин для добавления UUID первичного ключа"""

    id: Mapped[UUIDType] = mapped_column(
        UUIDTypeDecorator(),
        default=uuid4,
        primary_key=True,
        index=True,
        comment='Уникальный идентификатор'
    )
