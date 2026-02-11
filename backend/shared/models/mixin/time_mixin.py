""" Миксин """


import typing as t
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Миксин для добавления временных меток с timezone"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment='Время создания записи'
    )
    updated_at: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        comment='Время последнего обновления'
    )
