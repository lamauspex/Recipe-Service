""" Базовые схемы для переиспользования """

from pydantic import BaseModel, field_validator

from backend.user_service.src.schemas.validators import (
    NameValidator,
    PasswordSchemaValidator
)


class PasswordValidatedModel(BaseModel):
    """ Базовая схема с валидацией пароля """

    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Валидация сложности пароля"""

        is_valid, errors = PasswordSchemaValidator.validate(v)

        if not is_valid:
            raise ValueError('. '.join(errors))
        return v


class NameValidatedModel(BaseModel):
    """ Базовая схема с валидацией имени """

    user_name: str

    @field_validator('user_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Валидация имени"""

        is_valid, errors = NameValidator.validate(v)

        if not is_valid:
            raise ValueError('. '.join(errors))
        return v
