""" Схемы для входящих запросов """

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Вход пользователя"""

    email: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Обновление токена"""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Выход из системы"""

    refresh_token: str
