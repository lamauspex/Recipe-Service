from backend.database.schemas import (
    UserBase,
    UserCreate as BaseUserCreate,
    UserUpdate as BaseUserUpdate,
    UserResponse as BaseUserResponse,
    Token as BaseToken,
    TokenData as BaseTokenData
)

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

"""
Схемы Pydantic для user-service
Наследуются от базовых схем из backend.database.schemas
"""


class UserCreate(BaseUserCreate):
    """Схема для создания пользователя"""
    email: EmailStr

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        if not any(c.isupper() for c in v):
            raise ValueError(
                'Пароль должен содержать хотя бы одну заглавную букву')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v


class UserUpdate(BaseUserUpdate):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    bio: Optional[str] = None


class UserResponse(BaseUserResponse):
    """Схема ответа с данными пользователя"""
    bio: Optional[str] = None

    model_config = {'from_attributes': True}


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    username: str
    password: str


class Token(BaseToken):
    """Схема токена доступа"""
    pass


class TokenData(BaseTokenData):
    """Схема данных из токена"""
    pass


class RefreshTokenRequest(BaseModel):
    """Схема для обновления токена"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Схема для сброса пароля"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Схема для подтверждения сброса пароля"""
    token: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        if not any(c.isupper() for c in v):
            raise ValueError(
                'Пароль должен содержать хотя бы одну заглавную букву')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v


# Для обратной совместимости с существующим кодом
__all__ = [
    'UserBase',
    'UserCreate',
    'UserUpdate',
    'UserResponse',
    'UserLogin',
    'Token',
    'TokenData',
    'RefreshTokenRequest',
    'PasswordResetRequest',
    'PasswordResetConfirm'
]
