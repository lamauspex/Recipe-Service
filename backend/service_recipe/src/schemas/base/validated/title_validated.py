"""
Валидатор названия рецепта
"""

import re
from typing import List, Tuple


class TitleValidator:
    """
    Валидатор названия рецепта

    Проверяет:
        - Минимальная длина: 2 символа
        - Максимальная длина: 50 символов
        - Допустимые символы: буквы, цифры, дефис, подчёркивание

    Attributes:
        MIN_LENGTH: Минимальная длина названия
        MAX_LENGTH: Максимальная длина названия
        ALLOWED_CHARS: Регулярное выражение для допустимых символов

    Example:
        >>> is_valid, errors = TitleValidator.validate("Борщ")
        >>> is_valid
        True
    """

    MIN_LENGTH = 2
    MAX_LENGTH = 150
    ALLOWED_CHARS = r'^[a-zA-Zа-яА-ЯёЁ0-9_\-\s]+$'

    @classmethod
    def validate(cls, name: str) -> Tuple[bool, List[str]]:
        """
        Валидация названия рецепта.

        Args:
            name: Название для проверки

        Returns:
            Tuple[bool, List[str]]: (валиден, ошибки)

        Example:
            >>> is_valid, errors = TitleValidator.validate("А")
            >>> is_valid
            False
        """

        errors = []
        name = name.strip()

        if len(name) < cls.MIN_LENGTH:
            errors.append(
                f"Название должно содержать минимум {cls.MIN_LENGTH} символа"
            )

        if len(name) > cls.MAX_LENGTH:
            errors.append(
                f"Название должно содержать максимум {cls.MAX_LENGTH} символов"
            )

        # Используем регулярное выражение
        if not re.match(cls.ALLOWED_CHARS, name):
            errors.append(
                "Название может содержать только буквы, "
                "цифры, дефис и подчёркивание"
            )

        return len(errors) == 0, errors
