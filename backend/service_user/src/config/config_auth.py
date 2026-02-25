""" Аутентификация и JWT """


from pydantic import Field
from .base import BaseConfig


class AuthConfig(BaseConfig):
    """ Конфигурация АУТЕНТИФИКАЦИЯ И БЕЗОПАСНОСТЬ """

    ALGORITHM: str = Field(
        description="Проверка пароля"
    )
    SECRET_KEY: str = Field(
        description="Секретный ключ для JWT"
    )

    # JWT конфигурация
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        description="Загузай сюда сон"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        description="40 кликов"
    )
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = Field(
        description="тут так"
    )
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = Field(
        description="и тут"
    )

    # Безопасность
    MAX_LOGIN_ATTEMPTS: int = Field(
        description="Максимум попыток входа"
    )
    LOGIN_ATTEMPT_WINDOW_MINUTES: int = Field(
        description="Окно для подсчета попыток"
    )
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = Field(
        description="Время блокировки"
    )

    # Токены
    JTI_LENGTH: int = Field(description="Индивидуальные буковцы")
    TOKEN_LENGTH: int = Field(
        description="Максимально возможное количество знаков")

    # Пароли
    MIN_PASSWORD_LENGTH: int = Field(
        description="Минимальная длина пароля"
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

    # RATE LIMITING
    RATE_LIMIT_ENABLED: bool = Field(
        description="Включить rate limiting"
    )
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        description="Запросов в минуту"
    )
    RATE_LIMIT_REQUESTS_PER_HOUR: int = Field(
        description="Запросов в час"
    )
    RATE_LIMIT_BLOCK_DURATION: int = Field(
        description=" "
    )
    RATE_LIMIT_WINDOW_SECONDS: int = Field(
        description="Сколько секунд"
    )

    RATE_LIMIT_BURST_SIZE: int = Field(
        description="Кол-во запросов"
    )
