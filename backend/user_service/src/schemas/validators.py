""" Валидаторы для Pydantic схем """

import re
from typing import List, Tuple

from pydantic import field_validator


class PasswordSchemaValidator:
    """ Валидатор сложности пароля для использования в схемах """

    COMMON_PASSWORDS = [
        "password", "123456", "qwerty", "admin", "letmein",
        "monkey", "1234567890", "abc123", "password1", "12345678",
        "12345", "1234567", "iloveyou", "1234", "password123"
    ]

    @classmethod
    def validate(cls, password: str) -> Tuple[bool, List[str]]:
        """ Валидация пароля, возвращает (is_valid, errors) """

        errors = []

        if len(password) < 8:
            errors.append("Пароль должен содержать минимум 8 символов")

        if not re.search(r'[A-Z]', password):
            errors.append("Пароль должен содержать заглавные буквы")

        if not re.search(r'\d', password):
            errors.append("Пароль должен содержать цифры")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Пароль должен содержать специальные символы")

        if password.lower() in cls.COMMON_PASSWORDS:
            errors.append("Пароль слишком простой")

        return len(errors) == 0, errors


class NameValidator:

    @field_validator('user_name')
    @classmethod
    def validate_user_name(cls, v):

        if not v or len(v.strip()) < 3:
            raise ValueError(
                'Имя пользователя должно содержать минимум 3 символа'
            )

        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                'Имя пользователя может содержать только буквы, '
                'цифры, дефис и подчёркивание'
            )
        return v.strip()
