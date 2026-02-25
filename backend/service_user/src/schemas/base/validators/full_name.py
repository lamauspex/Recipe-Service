import regex as re
from typing import List, Tuple


class FullNameValidator:
    """ Валидатор полного имени """

    @classmethod
    def validate(cls, full_name: str) -> Tuple[bool, List[str]]:
        """ Валидация полного имени, возвращает (is_valid, errors) """

        errors = []

        full_name = full_name.strip()

        if len(full_name) < 2:
            errors.append('Полное имя должно содержать минимум 2 символа')

        if len(full_name) > 100:
            errors.append('Полное имя не должно превышать 100 символов')

        # Проверка на наличие хотя бы двух слов (имя и фамилия)
        if len(full_name.split()) < 2:
            errors.append(
                'Укажите имя и фамилию (минимум два слова)'
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
        """ Нормализация полного имени (удаление лишних пробелов) """
        return ' '.join(full_name.strip().split())
