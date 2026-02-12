""" Базовые схемы для переиспользования """

from typing import Optional
from pydantic import BaseModel, field_validator

from .validators import (
    HashedPasswordValidator,
    FullNameValidator,
    EmailValidator,
    NameValidator,
    PasswordSchemaValidator,
    RoleNameValidator,
    BooleanValidator,
    DateTimeValidator
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


class EmailValidatedModel(BaseModel):
    """ Базовая схема с валидацией email """

    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """ Валидация и нормализация email """

        is_valid, errors = EmailValidator.validate(v)

        if not is_valid:
            raise ValueError('. '.join(errors))

        return EmailValidator.normalize(v)


class FullNameValidatedModel(BaseModel):
    """ Базовая схема с валидацией полного имени """

    full_name: Optional[str] = None

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """ Валидация и нормализация полного имени """

        if v is not None:
            is_valid, errors = FullNameValidator.validate(v)

            if not is_valid:
                raise ValueError('. '.join(errors))

            return FullNameValidator.normalize(v)

        return v


class HashedPasswordValidatedModel(BaseModel):
    """ Базовая схема с валидацией хешированного пароля """

    hashed_password: str

    @field_validator('hashed_password')
    @classmethod
    def validate_hashed_password(cls, v: str) -> str:
        """ Проверка, что пароль действительно хеширован """

        is_valid, errors = HashedPasswordValidator.validate(v)

        if not is_valid:
            raise ValueError('. '.join(errors))

        return v


# ========== Общие валидационные модели ==========

class BooleanValidatedModel(BaseModel):
    """ Базовая схема для валидации boolean полей """

    is_active: bool = True
    is_verified: bool = False

    @field_validator('is_active', 'is_verified')
    @classmethod
    def validate_boolean_fields(cls, v: bool) -> bool:
        """ Проверка типа boolean полей """
        return BooleanValidator.validate(v)


class DateTimeValidatedModel(BaseModel):
    """ Базовая схема для валидации datetime полей """

    from datetime import datetime

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @field_validator('created_at', 'updated_at', 'deleted_at')
    @classmethod
    def validate_datetime_fields(
        cls,
        v: Optional[datetime]
    ) -> Optional[datetime]:
        """ Проверка типа datetime полей """
        return DateTimeValidator.validate(v)


class RoleNameValidatedModel(BaseModel):
    """ Базовая схема для валидации имени роли """

    role_name: str = "user"

    @field_validator('role_name')
    @classmethod
    def validate_role_name(cls, v: str) -> str:
        """ Валидация имени роли """
        return RoleNameValidator.validate(v)
