""" Валидатор хешированного пароля """


from typing import List, Tuple


class HashedPasswordValidator:
    """
    Валидатор хешированного пароля

    Проверяет:
        - Хеш не пустой
        - Используется алгоритм argon2
        - Минимальная длина хеша

    Настройки алгоритма хранятся в PasswordService

    Attributes:
        ALGORITHM: Алгоритм хеширования (argon2)
        MIN_LENGTH: Минимальная длина хеша

    Example:
        >>> is_valid, errors = HashedPasswordValidator.validate("$argon2...")
        >>> is_valid
        True
    """

    ALGORITHM = '$argon2'
    MIN_LENGTH = 50

    @classmethod
    def validate(cls, hashed_password: str) -> Tuple[bool, List[str]]:
        """
        Проверка, что пароль действительно хеширован
        Args:
            hashed_password: Хешированный пароль для проверки

        Returns:
            Tuple[bool, List[str]]: (валиден, ошибки)

        Example:
            >>> is_valid, errors = HashedPasswordValidator.validate(
                "$argon2$..."
                )
            >>> is_valid
            True
        """

        errors = []

        # Ранний выход если пароль пустой
        if not hashed_password or not hashed_password.strip():
            errors.append(
                'Хешированный пароль не может быть пустым'
            )

        # Проверка алгоритма
        if not hashed_password.startswith(cls.ALGORITHM):
            errors.append(f"Пароль должен быть хеширован ({cls.ALGORITHM})")

        # Проверка минимальной длины
        if len(hashed_password) < cls.MIN_LENGTH:
            errors.append("Хешированный пароль имеет некорректный формат")

        return len(errors) == 0, errors
