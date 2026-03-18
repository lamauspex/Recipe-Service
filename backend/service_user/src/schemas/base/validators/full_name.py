""" Валидатор полного имени пользователя """


import regex as re
from typing import List, Tuple


class FullNameValidator:
    """
    Валидатор полного имени пользователя

    Проверяет:
    - Минимальную длину: 2 символа
    - Максимальную длину: 100 символов
    - Наличие минимум двух слов (имя и фамилия)
    - Допустимые символы: буквы, пробелы, дефисы

    Attributes:
        MIN_LENGTH: Минимальная длина
        MAX_LENGTH: Максимальная длина
        MIN_WORDS: Минимальное количество слов

    Example:
        >>> is_valid, errors = FullNameValidator.validate("John Doe")
        >>> is_valid
        True
    """

    MIN_LENGTH = 2
    MAX_LENGTH = 100
    MIN_WORDS = 2

    @classmethod
    def validate(cls, full_name: str) -> Tuple[bool, List[str]]:
        """
        Валидация полного имени

        Args:
            full_name: Полное имя для проверки

        Returns:
            Tuple[bool, List[str]]: (валиден, ошибки)
        """

        errors = []

        full_name = full_name.strip()

        if len(full_name) < cls.MIN_LENGTH:
            errors.append(
                f'Полное имя должно содержать минимум {cls.MIN_LENGTH} символа'
            )

        if len(full_name) > cls.MAX_LENGTH:
            errors.append(
                f'Полное имя не должно превышать {cls.MAX_LENGTH} символов'
            )

        # Проверка на наличие хотя бы двух слов (имя и фамилия)
        if len(full_name.split()) < cls.MIN_WORDS:
            errors.append(
                f'Укажите имя и фамилию (минимум {cls.MIN_WORDS} слов(а))'
            )

        # Проверка на допустимые символы (буквы, пробелы, дефисы)
        if not re.match(
            r'^[\p{L}\s\-]+$',
            full_name,
            flags=re.UNICODE
        ):
            errors.append(
                'Полное имя может содержать только буквы, пробелы и дефисы'
            )

        return len(errors) == 0, errors

    @classmethod
    def normalize(cls, full_name: str) -> str:
        """
        Нормализация полного имени
        Удаляет лишние пробелы, приводит к нужному формату.

        Args:
            full_name: Полное имя для нормализации

        Returns:
            str: Нормализованное полное имя

        Example:
            >>> FullNameValidator.normalize("  John   Doe  ")
            'John Doe'
        """
        return ' '.join(full_name.strip().split())
