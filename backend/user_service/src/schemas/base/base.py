""" Базовые схемы для переиспользования """

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

from .validators import (
    HashedPasswordValidator,
    FullNameValidator,
    EmailValidator,
    NameValidator,
    PasswordSchemaValidator,
    RoleNameValidator
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

class RoleNameValidatedModel(BaseModel):
    """ Базовая схема для валидации имени роли """

    role_name: str = "user"

    @field_validator('role_name')
    @classmethod
    def validate_role_name(cls, v: str) -> str:
        """ Валидация имени роли """
        return RoleNameValidator.validate(v)


# ========== Специализированные модели для User ==========

class UserStatusModel(BaseModel):
    """
    Базовая схема для статуса пользователя.

    Содержит только те поля, которые есть в модели User.
    """

    is_active: bool = True
    email_verified: bool = False


class UserTimestampsModel(BaseModel):
    """
    Базовая схема для временных меток пользователя.

    Содержит только те поля, которые есть в модели User
    (нет deleted_at).
    """

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
