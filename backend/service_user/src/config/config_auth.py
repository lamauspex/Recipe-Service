""" Аутентификация и JWT """


from pydantic import Field
from .base import BaseConfig


class AuthConfig(BaseConfig):
    """ Конфигурация АУТЕНТИФИКАЦИЯ И БЕЗОПАСНОСТЬ """

    ALGORITHM: str = Field(description="Проверка пароля")
    SECRET_KEY: str = Field(description="Секретный ключ для JWT")

    # JWT конфигурация
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(description="")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(description="40 кликов")

    # Пароли
    MIN_PASSWORD_LENGTH: int = Field(
        description="Минимальная длина пароля"
    )
    MAX_PASSWORD_LENGTH: int = Field(
        description="Максимальная длина пароля"
    )
    REQUIRE_DIGITS: bool = Field(
        description="Требуются цифры"
    )
    REQUIRE_UPPERCASE: bool = Field(
        description="Требуются заглавные"
    )
    REQUIRE_LOWERCASE: bool = Field(
        description="Требуются строчные"
    )
    REQUIRE_SPECIAL_CHARS: bool = Field(
        description="Требуются спецсимволы"
    )
