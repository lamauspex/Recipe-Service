"""
Модель для отслеживания попыток входа
Помогает обеспечить безопасность и предотвратить brute force атаки
"""


import typing as t
from sqlalchemy import (
    String,
    Boolean,
    ForeignKey
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)


from backend.user_service.src.models.base_models import BaseModel


class LoginAttempt(BaseModel):
    """Модель для отслеживания попыток входа"""

    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=True,
        index=True,
        comment='ID пользователя (если пользователь существует)'
    )

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment='Email, с которого была попытка входа'
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        comment='IP адрес, с которого была попытка'
    )

    user_agent: Mapped[t.Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment='User Agent браузера'
    )

    is_successful: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment='Успешна ли попытка входа'
    )

    failure_reason: Mapped[t.Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment='Причина неудачи неверный пароль'
    )

    # Связь с пользователем
    user = relationship(
        "User",
        back_populates="login_attempts"
    )

    def __repr__(self) -> str:
        return (
            f"<LoginAttempt(id={self.id}, "
            f"email='{self.email}', "
            f"ip='{self.ip_address}', "
            f"successful={self.is_successful})>"
        )
