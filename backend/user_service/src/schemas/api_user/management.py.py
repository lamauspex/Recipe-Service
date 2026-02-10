

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator
)
from typing import Optional
from uuid import UUID
from datetime import datetime

from back.schemas.user_roles import UserRole
from backend.user_service.duble_service_dtoschemas.core.validator_password import PasswordValidator


class UserBase(BaseModel):
    """Базовая схема пользователя"""

    user_name: str
    email: EmailStr
    full_name: Optional[str] = None


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""

    id: UUID
    bio: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AdminUserResponse(UserResponse):
    """Схема для ответа админов"""

    email_verified: bool
    last_login: Optional[datetime] = None
    login_count: int = Field(
        default=0,
        ge=0
    )

    model_config = ConfigDict(from_attributes=True)


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
        validator = PasswordValidator()
        is_valid, errors = validator.validate_password(v)
        if not is_valid:
            raise ValueError('; '.join(errors))
        return v


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""

    id: UUID
    bio: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
