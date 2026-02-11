from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

from backend.user_service.src.schemas.validators import (
    NameValidator,
    PasswordSchemaValidator
)


class UserCreate(BaseModel):
    """Схема для регистрации пользователя"""

    user_name: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Валидация сложности пароля"""
        is_valid, errors = PasswordSchemaValidator.validate(v)
        if not is_valid:
            raise ValueError('. '.join(errors))
        return v

    @field_validator('user_name')
    @classmethod
    def validate_user_name(cls, v: str) -> str:
        """Валидация имени"""
        is_valid, errors = NameValidator.validate(v)
        if not is_valid:
            raise ValueError('. '.join(errors))
        return v
