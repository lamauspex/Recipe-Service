"""
Единая система исключений для User Service
"""

from .base import (
    AppException,
    ConflictException,
    NotFoundException,
    ValidationException,
)
from .auth import (
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException,
)

__all__ = [
    # Базовые
    "AppException",
    # Auth
    "InvalidCredentialsException",
    "InvalidTokenException",
    "TokenExpiredException",
    # Общие
    "ConflictException",
    "NotFoundException",
    "ValidationException",
]
