""" Миксин """


import typing as t
from datetime import datetime
from sqlalchemy import DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Миксин для добавления временных меток с timezone"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("timezone('utc', now())"),
        comment='Время создания записи'
    )
    updated_at: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=text("timezone('utc', now())"),
        server_default=text("timezone('utc', now())"),
        comment='Время последнего обновления'
    )
