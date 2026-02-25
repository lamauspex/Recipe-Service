
from typing import List, Tuple


class HashedPasswordValidator:
    """ Валидатор хешированного пароля """

    @classmethod
    def validate(cls, hashed_password: str) -> Tuple[bool, List[str]]:
        """ Проверка, что пароль действительно хеширован """

        errors = []

        if not hashed_password or not hashed_password.strip():
            errors.append(
                'Хешированный пароль не может быть пустым'
            )

        # Проверка на хешироверку на argon2
        if not hashed_password.startswith('$argon2'):
            errors.append(
                'Пароль должен быть хеширован (argon2)'
            )

        # Минимальная длина argon2 хеша - 60 символов
        if len(hashed_password) < 50:
            errors.append(
                'Хешированный пароль имеет некорректный формат'
            )

        return len(errors) == 0, errors
