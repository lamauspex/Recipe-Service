

import re
from typing import List, Tuple


class PasswordValidator:

    COMMON_PASSWORDS = [
        "password",
        "123456",
        "qwerty",
        "admin",
        "letmein",
        "monkey",
        "1234567890",
        "abc123",
        "password1",
        "12345678",
        "12345",
        "1234567",
        "iloveyou",
        "1234",
        "password123"
    ]

    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, List[str]]:
        """Расширенная валидация пароля"""

        errors = []

        # Длина
        if len(password) < 8:
            errors.append("Пароль должен содержать минимум 8 символов")

        # Заглавные буквы
        if not re.search(r'[A-Z]', password):
            errors.append("Пароль должен содержать заглавные буквы")

        # Цифры
        if not re.search(r'\d', password):
            errors.append("Пароль должен содержать цифры")

        # Специальные символы
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Пароль должен содержать специальные символы")

        # Пароль не должен содержать часть email адреса
        # (эта проверка должна выполняться в вызывающем коде с передачей email)

        # Common passwords
        if password.lower() in cls.COMMON_PASSWORDS:
            errors.append("Пароль слишком простой")

        return len(errors) == 0, errors

    def calculate_strength(self, password: str) -> int:
        """Расчет силы пароля (0-100)"""

        score = 0

        # Длина
        if len(password) >= 8:
            score += 20
        if len(password) >= 12:
            score += 10

        # Разнообразие символов
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'\d', password):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 10

        # Бонусы
        if len(password) >= 16:
            score += 10
        if not self._has_sequential_chars(password):
            score += 10
        if not self._has_repeated_chars(password):
            score += 10

        return min(score, 100)
