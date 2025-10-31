
"""
Схемы Pydantic для user-service
Автономная реализация без зависимостей от общих модулей
"""

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str

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


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: UUID
    bio: Optional[str] = None
    is_admin: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    username: str
    password: str


class Token(BaseModel):
    """Схема токена доступа"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str


class TokenData(BaseModel):
    """Схема данных из токена"""
    username: Optional[str] = None
    user_id: Optional[UUID] = None
    is_admin: bool = False


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
