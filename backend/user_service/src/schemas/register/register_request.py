from pydantic import BaseModel, ConfigDict

from backend.user_service.src.schemas.base import (
    PasswordValidatedModel,
    NameValidatedModel,
    FullNameValidatedModel,
    EmailValidatedModel
)


class UserCreate(
        BaseModel,
        PasswordValidatedModel,
        NameValidatedModel,
        FullNameValidatedModel,
        EmailValidatedModel
):

    """
    Схема для регистрации пользователя
    Наследует валидацию от базовых схем:
    - PasswordValidatedModel: валидация сложности пароля
    - NameValidatedModel: валидация имени пользователя
    - FullNameValidatedModel: валидация и нормализация полного имени
    - EmailValidatedModel: валидация email
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "user_name": "john_doe",
                    "email": "john@example.com",
                    "password": "SecurePass123!",
                    "full_name": "John Doe"
                }
            ]
        }
    )
