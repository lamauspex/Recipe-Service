from typing import List, Tuple


class TitleValidator:
    """ Валидатор названия рецепта """

    MIN_LENGTH = 2
    MAX_LENGTH = 50

    @classmethod
    def validate(cls, name: str) -> Tuple[bool, List[str]]:

        errors = []

        if not name or len(name.strip()) < cls.MIN_LENGTH:
            errors.append(
                f'Название должно содержать минимум {cls.MIN_LENGTH} символа'
            )

        if not name or len(name.strip()) > cls.MAX_LENGTH:
            errors.append(
                f'Название должно содержать максимум {cls.MAX_LENGTH} символов'
            )

        if not name.replace('_', '').replace('-', '').isalnum():
            errors.append(
                'Название может содержать только буквы, '
                'цифры, дефис и подчёркивание'
            )

        return len(errors) == 0, errors
