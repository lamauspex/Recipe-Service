""" Миксин """


from datetime import datetime
from sqlalchemy import DateTime, text
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Миксин для добавления временных меток с timezone"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("timezone('utc', now())"),
        nullable=False,
        comment='Время создания записи'
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=text("timezone('utc', now())"),
        server_default=text("timezone('utc', now())"),
        nullable=True,
        comment='Время последнего обновления'
    )
