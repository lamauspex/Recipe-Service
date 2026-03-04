""" Внутренние DTO """

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TokenPair(BaseModel):
    """Пара токенов (сервисный слой)"""

    access_token: str
    refresh_token: str


class AuthResult(BaseModel):
    """Результат аутентификации"""

    user_id: UUID
    user_name: str
    role: str


class RefreshTokenData(BaseModel):
    """Данные для refresh токена"""

    user_id: UUID
    token: str
    expires_at: datetime
