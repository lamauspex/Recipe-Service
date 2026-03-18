""" Валидатор имени пользователя """

import re
from typing import List, Tuple


class NameValidator:
    """
    Валидатор имени пользователя (user_name)

    Проверяет:
    - Минимальную длину: 3 символа
    - Допустимые символы: буквы, цифры, дефис, подчёркивание

    Attributes:
        MIN_LENGTH: Минимальная длина имени
        MAX_LENGTH: Максимальная длина имени
        ALLOWED_CHARS: Допустимые символы (регулярное выражение)

    Example:
        >>> is_valid, errors = NameValidator.validate("john_doe")
        >>> is_valid
        True
    """

    MIN_LENGTH = 3
    MAX_LENGTH = 50
    ALLOWED_CHARS = r'^[a-zA-Z0-9_-]+$'

    @classmethod
    def validate(cls, name: str) -> Tuple[bool, List[str]]:
        """
        Валидация имени пользователя

        Args:
            name: Имя для проверки

        Returns:
            Tuple[bool, List[str]]: (валиден, ошибки)

        Example:
            >>> is_valid, errors = NameValidator.validate("ab")
            >>> is_valid
            False
        """

        errors = []

        if not name or len(name.strip()) < cls.MIN_LENGTH:
            errors.append(
                f"Имя пользователя должно содержать минимум "
                f"{cls.MIN_LENGTH} символа"
            )

        if len(name) > cls.MAX_LENGTH:
            errors.append(
                f"Имя пользователя не должно превышать "
                f"{cls.MAX_LENGTH} символов"
            )

        if not re.match(cls.ALLOWED_CHARS, name):
            errors.append(
                'Имя пользователя может содержать только буквы, '
                'цифры, дефис и подчёркивание'
            )

        return len(errors) == 0, errors
