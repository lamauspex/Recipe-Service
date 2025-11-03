"""
Модели для работы с refresh tokens
"""

from datetime import datetime
from sqlalchemy import (
    String, Boolean,
    DateTime, ForeignKey)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship)

from backend.services.user_service.models.base_models import (
    BaseModel, UUIDTypeDecorator)


class RefreshToken(BaseModel):
    """Модель refresh token для JWT аутентификации"""
    __tablename__ = "refresh_tokens"

    user_id: Mapped[str] = mapped_column(
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

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment='Время истечения'
    )

    # Связь с пользователем
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"
