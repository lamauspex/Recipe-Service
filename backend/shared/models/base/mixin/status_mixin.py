""" Миксин """

from sqlalchemy.orm import Mapped, mapped_column


class StatusMixin:
    """Миксин для добавления статуса активности"""

    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment='Флаг активности записи'
    )
