""" Валидатор сложности пароля """


import re
from typing import List, Optional, Tuple

from backend.service_user.src.config import AuthConfig


class PasswordSchemaValidator:
    """
    Валидатор сложности пароля

    Проверяет пароль на соответствие требованиям безопасности
    Конфигурация читается из AuthConfig (.env)

    Требования (из конфига):
        - MIN_PASSWORD_LENGTH: Минимальная длина
        - MAX_PASSWORD_LENGTH: Максимальная длина
        - REQUIRE_UPPERCASE: Заглавные буквы
        - REQUIRE_LOWERCASE: Строчные буквы
        - REQUIRE_DIGITS: Цифры
        - REQUIRE_SPECIAL_CHARS: Специальные символы

    Attributes:
        COMMON_PASSWORDS: Список распространённых паролей для блокировки

    Example:
        >>> is_valid, errors = PasswordSchemaValidator.validate(
            "SecurePass123!"
            )
        >>> is_valid
        True
    """

    COMMON_PASSWORDS = [
        "password", "123456", "qwerty", "admin", "letmein",
        "monkey", "1234567890", "abc123", "password1", "12345678",
        "12345", "1234567", "iloveyou", "1234", "password123"
    ]

    @classmethod
    def _get_config(cls) -> AuthConfig:
        """ Получение конфига через контейнер (lazy import) """
        return AuthConfig()

    @classmethod
    def validate(
        cls,
        password: str
    ) -> Tuple[bool, List[str]]:
        """
        Валидация пароля

        Args:
            password: Пароль для проверки

        Returns:
            Tuple[bool, List[str]]: (валиден, ошибки)
        """

        config = cls._get_config()
        errors = []

        # Проверка минимальной длины
        if len(password) < config.MIN_PASSWORD_LENGTH:
            errors.append(
                f"Пароль должен содержать минимум "
                f"{config.MIN_PASSWORD_LENGTH} символов"
            )

        # Проверка максимальной длины
        if len(password) > config.MAX_PASSWORD_LENGTH:
            errors.append(
                f"Пароль должен содержать максимум "
                f"{config.MAX_PASSWORD_LENGTH} символов"
            )

        # Проверка заглавных букв
        if config.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Пароль должен содержать заглавные буквы")

        # Проверка строчных букв
        if config.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Пароль должен содержать строчные буквы")

        # Проверка цифр
        if config.REQUIRE_DIGITS and not re.search(r'\d', password):
            errors.append("Пароль должен содержать цифры")

        # Проверка специальных символов
        if config.REQUIRE_SPECIAL_CHARS and not re.search(
            r'[!@#$%^&*(),.?":{}|<>]',
            password
        ):
            errors.append("Пароль должен содержать специальные символы")

        # Проверка на распространённые пароли
        if password.lower() in cls.COMMON_PASSWORDS:
            errors.append("Пароль слишком простой")

        return len(errors) == 0, errors
