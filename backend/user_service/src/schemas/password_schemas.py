
from pydantic import (
    BaseModel,
    EmailStr,
    field_validator
)

from user_service.utils import PasswordValidator


class UserLogin(BaseModel):
    """Схема для входа пользователя"""

    user_name: str
    password: str


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
