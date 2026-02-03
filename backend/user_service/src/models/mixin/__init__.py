""" Mixins package - удобные импорты миксинов """

from .key_mixin import UUIDPrimaryKeyMixin
from .time_mixin import TimestampMixin
from .status_mixin import StatusMixin

__all__ = [
    "UUIDPrimaryKeyMixin",
    "TimestampMixin",
    "StatusMixin"
]
