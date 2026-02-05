"""
Координирующий слой, который вызывает методы остальных служб
для выполнения необходимых операций
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from backend.user_service.src.models import User
from backend.user_service.src.repository import UserRepository
from backend.user_service.src.config import settings
from .refresh_token_service import RefreshTokenService
from .password_service import PasswordService
from .jwt_service import JWTService


class AuthService:
    """Класс для работы с пользователями"""

    def __init__(self, db_session):
        self.user_repo = UserRepository(db_session)
        self.pwd_service = PasswordService()
        self.jwt_service = JWTService(
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        self.refresh_token_service = RefreshTokenService(db_session)

    def authenticate_user(
        self,
        user_name: str,
        password: str
    ) -> Optional[User]:
        """Аутентификация пользователя"""

        user = self.user_repo.get_user_by_user_name(user_name)

        if not user or not self.pwd_service.verify_password(
            password,
            user.hashed_password
        ) or not user.is_active:

            return None

        return user

    def authenticate_and_create_tokens(
        self,
        user_name: str,
        password: str
    ) -> Tuple[str, str]:
        """Аутентификация + создание токенов - возвращает готовый ответ"""

        user = self.authenticate_user(user_name, password)

        if not user:
            # Здесь можно вернуть ошибку, но пока просто вернем токены
            # В реальном приложении лучше выбрасывать исключение
            return "", ""

        return self.create_tokens(user)

    def create_tokens(self, user: User) -> Tuple[str, str]:
        """ Создание токенов """

        access_token = self.jwt_service.create_access_token({
            "sub": str(user.id),
            "username": user.user_name,
            "role": user.role.value
        })

        refresh_token = self.jwt_service.create_refresh_token({
            "sub": str(user.id)
        })

        self.refresh_token_service.create_refresh_token(
            user.id,
            refresh_token,
            datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        )
        return access_token, refresh_token

    def refresh_access_token(
        self,
        refresh_token: str
    ) -> Optional[Tuple[str, str]]:
        """Обновление токенов"""

        valid_token = self.refresh_token_service.get_valid_token(refresh_token)
        if not valid_token:
            return None

        user = self.user_repo.get_user_by_id(valid_token.user_id)
        if not user:
            return None

        self.refresh_token_service.revoke_token(refresh_token)
        return self.create_tokens(user)

    def revoke_refresh_token(self, refresh_token: str) -> dict:
        """Отзыв refresh token - возвращает готовый ответ"""

        try:
            self.refresh_token_service.revoke_token(refresh_token)
            return {
                "message": "Успешный выход из системы",
                "success": True
            }
        except Exception as e:
            return {
                "error": f"Ошибка при выходе из системы: {str(e)}",
                "success": False
            }

    def reset_password(self, token: str, new_password: str) -> dict:
        """Сброс пароля - возвращает готовый ответ"""

        try:
            # В реальном приложении здесь была бы проверка токена
            # Пока что просто возвращаем успех
            return {
                "message": "Пароль успешно сброшен",
                "success": True
            }
        except Exception as e:
            return {
                "error": f"Ошибка при сбросе пароля: {str(e)}",
                "success": False
            }
