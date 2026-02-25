""" Общие валидаторы для Pydantic схем """

from datetime import datetime
from typing import Optional


class RoleNameValidator:
    """ Валидатор имени роли """

    ALLOWED_ROLES = {'user', 'moderator', 'admin'}

    @classmethod
    def validate(cls, role_name: str) -> str:
        """
        Валидация имени роли.

        Args:
            role_name: Имя роли для проверки

        Returns:
            str: Нормализованное имя роли (в нижнем регистре)

        Raises:
            ValueError: Если роль недопустима
        """
        role_name = role_name.strip().lower()

        if role_name not in cls.ALLOWED_ROLES:
            raise ValueError(
                f'Недопустимая роль. Допустимые значения: '
                f'{", ".join(sorted(cls.ALLOWED_ROLES))}'
            )

        return role_name


class BooleanValidator:
    """ Валидатор boolean полей """

    @classmethod
    def validate(cls, value: bool) -> bool:
        """
        Проверка типа boolean.

        Args:
            value: Значение для проверки

        Returns:
            bool: Проверенное значение

        Raises:
            ValueError: Если значение не является bool
        """
        if not isinstance(value, bool):
            raise ValueError('Значение должно быть boolean')
        return value


class DateTimeValidator:
    """ Валидатор datetime полей """

    @classmethod
    def validate(cls, value: Optional[datetime]) -> Optional[datetime]:
        """
        Проверка типа datetime.

        Args:
            value: Значение для проверки

        Returns:
            Optional[datetime]: Проверенное значение

        Raises:
            ValueError: Если значение не является datetime или None
        """
        if value is not None and not isinstance(value, datetime):
            raise ValueError('Значение должно быть datetime или None')
        return value
