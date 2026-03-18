"""
Модуль схем аутентификации

Содержит:
- requests: Схемы входящих запросов (Login, Refresh, Logout)
- responses: Схемы ответов API (Token, Message)
- auth_dto: Внутренние DTO для сервисного слоя
"""

from .auth_dto import (
    TokenPairDTO,
    AuthResultDTO,
    RefreshTokenDataDTO
)
from .requests import (
    LoginRequest,
    RefreshTokenRequest,
    LogoutRequest
)
from .responses import (
    TokenResponse,
    MessageResponse
)

__all__ = [
    # DTO (внутренние)
    "TokenPairDTO",
    "AuthResultDTO",
    "RefreshTokenDataDTO",
    # Запросы
    "LoginRequest",
    "RefreshTokenRequest",
    "LogoutRequest",
    # Ответы
    "TokenResponse",
    "MessageResponse"
]
