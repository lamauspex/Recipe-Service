
from typing import List, Tuple


class DescriptionValidator:
    """
    Валидатор для проверки описания
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

        if not description or len(description.strip()) < cls.MIN_LENGTH:
            errors.append(
                f'Описание должно содержать не менее {cls.MIN_LENGTH} символов'
            )

        if len(description) > cls.MAX_LENGTH:
            errors.append(
                f'Описание не может содержать более {cls.MAX_LENGTH} символов'
            )

        return len(errors) == 0, errors
