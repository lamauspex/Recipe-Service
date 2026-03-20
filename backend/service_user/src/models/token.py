"""
Модель refresh token для auth-service
"""

from datetime import datetime
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from uuid import UUID as UUIDType

from backend.shared.models.base_model import BaseModel


class RefreshToken(BaseModel):
    """Модель refresh token для JWT аутентификации"""

    user_id: Mapped[UUIDType] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
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

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment='Время истечения'
    )

    # Связь с пользователем
    user = relationship(
        "User",
        back_populates="refresh_tokens"
    )
