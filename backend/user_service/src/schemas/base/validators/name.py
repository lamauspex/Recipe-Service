
from typing import List, Tuple


class NameValidator:
    """ Валидатор имени пользователя """

    @classmethod
    def validate(cls, name: str) -> Tuple[bool, List[str]]:
        """ Валидация имени, возвращает (is_valid, errors) """

        errors = []

        if not name or len(name.strip()) < 3:
            errors.append(
                'Имя пользователя должно содержать минимум 3 символа'
            )

        if not name.replace('_', '').replace('-', '').isalnum():
            errors.append(
                'Имя пользователя может содержать только буквы, '
                'цифры, дефис и подчёркивание'
            )

        return len(errors) == 0, errors
