import re
from typing import List, Tuple


class EmailValidator:
    """ Валидатор email """

    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    @classmethod
    def validate(cls, email: str) -> Tuple[bool, List[str]]:
        """ Валидация email, возвращает (is_valid, errors) """

        errors = []

        if not email or not email.strip():
            errors.append('Email не может быть пустым')

        if not cls.EMAIL_REGEX.match(email):
            errors.append('Некорректный формат email')

        return len(errors) == 0, errors

    @classmethod
    def normalize(cls, email: str) -> str:
        """ Нормализация email (приведение к нижнему регистру) """
        return email.strip().lower()
