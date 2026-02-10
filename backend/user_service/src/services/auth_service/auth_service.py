"""
Координирующий слой, который вызывает методы остальных служб
для выполнения необходимых операций
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from user_service.models import User
from user_service.repository import UserRepository
from user_service.config import settings
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

    def authenticate_and_create_tokens(
        self,
        user_name: str,
        password: str
    ) -> Optional[Tuple[str, str]]:
        """
        Аутентификация и создание токенов

        Возвращает: (access_token, refresh_token) или None при ошибке
        """
        # Шаг 1: Аутентификация пользователя
        user = self.authenticate_user(user_name, password)

        if not user:
            # Логирование неудачной попытки
            return None

        # Шаг 2: Создание токенов
        return self.create_tokens(user)

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
