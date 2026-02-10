from typing import Optional

from backend.user_service.duble_service_dtoschemas.models.user_models import User


class AuthValidator:
    """Валидатор аутентификационных данных"""

    @staticmethod
    def validate_user_for_auth(user: Optional[User]) -> bool:
        """
        Проверка, может ли пользователь аутентифицироваться

        Проверяет:
        - Пользователь существует
        - Пользователь активен (is_active)
        """

        if user is None:
            return False

        if not user.is_active:
            return False

        return True

    @staticmethod
    def validate_password_match(
        plain_password: str,
        hashed_password: str,
        password_service
    ) -> bool:
        """Проверка совпадения пароля"""

        return password_service.verify_password(
            plain_password,
            hashed_password
        )
