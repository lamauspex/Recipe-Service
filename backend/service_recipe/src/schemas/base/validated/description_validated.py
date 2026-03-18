"""
Валидатор описания рецепта
"""


from typing import List, Tuple


class DescriptionValidator:
    """
    Валидатор описания рецепта.

    Проверяет:
        - Минимальная длина: 5 символов
        - Максимальная длина: 500 символов

    Attributes:
        MIN_LENGTH: Минимальная длина описания
        MAX_LENGTH: Максимальная длина описания

    Example:
        >>> is_valid, errors = DescriptionValidator.validate("Вкусный борщ")
        >>> is_valid
        True
    """

    MIN_LENGTH = 5
    MAX_LENGTH = 500

    @classmethod
    def validate(cls, description: str) -> Tuple[bool, List[str]]:
        """
        Валидация описания, возвращает (is_valid, errors)

        Проверяет:
        - Минимальную длину (MIN_LENGTH)
        - Максимальную длину (MAX_LENGTH)
        """
        errors = []
        description = description.strip()

        if len(description) < cls.MIN_LENGTH:
            errors.append(
                f"Описание должно содержать не менее {cls.MIN_LENGTH} символов"
            )

        if len(description) > cls.MAX_LENGTH:
            errors.append(
                f"Описание не может содержать более {cls.MAX_LENGTH} символов"
            )

        return len(errors) == 0, errors
