""" Валидатор и нормализатор email """


import re
from typing import List, Tuple


class EmailValidator:
    """
    Валидатор и нормализатор email-адреса

    Проверяет:
        - Email не пустой
        - Корректный формат (RFC 5322 упрощённый)

    Нормализует:
        - Удаление пробелов по краям
        - Приведение к нижнему регистру

    Attributes:
        EMAIL_REGEX: Регулярное выражение для проверки формата email
        MAX_LENGTH: Максимальная длина email

    Example:
        >>> is_valid, errors = EmailValidator.validate("User@Example.com")
        >>> is_valid
        True
        >>> EmailValidator.normalize("  User@Example.COM ")
        'user@example.com'
    """

    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    MAX_LENGTH = 254

    @classmethod
    def validate(cls, email: str) -> Tuple[bool, List[str]]:
        """
        Валидация email

        Args:
            email: Email для проверки

        Returns:
            Tuple[bool, List[str]]: (валиден, ошибки)

        Example:
            >>> is_valid, errors = EmailValidator.validate("test@example.com")
            >>> is_valid
            True
            >>> is_valid, errors = EmailValidator.validate("invalid")
            >>> is_valid
            False
        """

        errors = []

        # Ранний выход если пустой
        if not email or not email.strip():
            errors.append("Email не может быть пустым")
            return False, errors

        # Проверка длины
        if len(email) > cls.MAX_LENGTH:
            errors.append(
                f"Email не должен превышать {cls.MAX_LENGTH} символов")

        # Проверка формата
        if not cls.EMAIL_REGEX.match(email):
            errors.append("Некорректный формат email")

        return len(errors) == 0, errors

    @classmethod
    def normalize(cls, email: str) -> str:
        """
        Нормализация email.

        Выполняет:
            - Удаление пробелов по краям
            - Приведение к нижнему регистру

        Args:
            email: Email для нормализации

        Returns:
            str: Нормализованный email

        Example:
            >>> EmailValidator.normalize("  John.Doe@Example.COM ")
            'john.doe@example.com'
        """
        return email.strip().lower()
