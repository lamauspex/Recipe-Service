""" Базовые схемы с валидаторами для переиспользования """

from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)

from .validators import (
    HashedPasswordValidator,
    FullNameValidator,
    EmailValidator,
    NameValidator,
    PasswordSchemaValidator,
    RoleNameValidator
)


class PasswordValidatedModel(BaseModel):
    """
    Базовая схема с валидацией пароля

    Используется для полей с паролем, который нужно проверить
    на соответствие требованиям сложности (конфиг из .env).

    Attributes:
        password: Пароль для валидации
    """

    model_config = ConfigDict(from_attributes=True)

    password: str = Field(..., description="Пароль пользователя")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Валидация сложности пароля"""

        is_valid, errors = PasswordSchemaValidator.validate(v)

        if not is_valid:
            raise ValueError('. '.join(errors))
        return v


class NameValidatedModel(BaseModel):
    """
    Базовая схема с валидацией имени пользователя

    Используется для поля user_name.
    Проверяет длину и допустимые символы.

    Attributes:
        user_name: Имя пользователя
    """

    model_config = ConfigDict(from_attributes=True)

    user_name: str = Field(..., description="Имя пользователя (user_name)")

    @field_validator('user_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """ Валидация имени """

        is_valid, errors = NameValidator.validate(v)

        if not is_valid:
            raise ValueError('. '.join(errors))
        return v


class EmailValidatedModel(BaseModel):
    """
    Базовая схема с валидацией email

    Проверяет формат и нормализует (нижний регистр)

    Attributes:
        email: Email пользователя
    """

    model_config = ConfigDict(from_attributes=True)

    email: str = Field(..., description="Email пользователя")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """ Валидация и нормализация email """
        is_valid, errors = EmailValidator.validate(v)

        if not is_valid:
            raise ValueError('. '.join(errors))

        return EmailValidator.normalize(v)


class FullNameValidatedModel(BaseModel):
    """
    Базовая схема с валидацией полного имени

    Используется для поля full_name (опционально)
    Проверяет формат и нормализует

    Attributes:
        full_name: Полное имя пользователя (опционально)
    """

    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str] = Field(
        default=None,
        description="Полное имя пользователя"
    )

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
    """
    Базовая схема с валидацией хешированного пароля

    Используется для проверки что пароль действительно
    хеширован алгоритмом argon2

    Attributes:
        hashed_password: Хешированный пароль
    """

    model_config = ConfigDict(from_attributes=True)

    hashed_password: str = Field(..., description="Хешированный пароль")

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
    """
    Базовая схема для валидации имени роли

    Проверяет что роль допустима (user, moderator, admin)

    Attributes:
        role_name: Имя роли пользователя
    """

    model_config = ConfigDict(from_attributes=True)

    role_name: str = Field(
        default="user",
        description="Роль пользователя (user, moderator, admin)"
    )

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
    Используется при создании/обновлении пользователя.

    Attributes:
        is_active: Активен ли аккаунт
        email_verified: Подтверждён ли email
    """

    model_config = ConfigDict(from_attributes=True)

    is_active: bool = Field(
        default=True,
        description="Активен ли аккаунт"
    )
    email_verified: bool = Field(
        default=False,
        description="Подтверждён ли email"
    )


class UserTimestampsModel(BaseModel):
    """
    Базовая схема для временных меток пользователя

    Содержит временные метки создания и обновления.
    Используется для ответа API.

    Attributes:
        created_at: Время создания записи
        updated_at: Время последнего обновления
    """

    model_config = ConfigDict(from_attributes=True)

    created_at: Optional[datetime] = Field(
        default=None,
        description="Время создания записи"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Время последнего обновления"
    )
