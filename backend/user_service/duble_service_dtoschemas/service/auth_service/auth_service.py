"""
Координирующий слой, который вызывает методы остальных служб
для выполнения необходимых операций
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from backend.user_service.duble_service_dtoschemas.core.service_jwt import JWTService
from backend.user_service.duble_service_dtoschemas.core.service_password import PasswordService
from backend.user_service.duble_service_dtoschemas.core.validator_auth import AuthValidator
from backend.user_service.duble_service_dtoschemas.models.user_models import User
from backend.user_service.duble_service_dtoschemas.protocols.user_repository import UserRepositoryProtocol
from backend.user_service.duble_service_dtoschemas.schemas.auth.auth_dto import TokenPairDTO
from backend.user_service.duble_service_dtoschemas.service.auth_service.mappers import AuthMapper


class AuthService:
    """ Сервис аутентификации """

    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        password_service: PasswordService = None,
        jwt_service: JWTService = None
    ):
        self.user_repo = user_repo
        self.password_service = password_service or PasswordService()
        self.jwt_service = jwt_service or JWTService()
        self.auth_validator = AuthValidator()
        self.mapper = AuthMapper()

    def authenticate_and_create_tokens(
        self,
        user_name: str,
        password: str
    ) -> Optional[TokenPairDTO]:
        """
        Аутентификация и создание токенов

        Возвращает: TokenPairDTO или None при ошибке
        """
        # Шаг 1: Аутентификация пользователя
        user = self.user_repo.get_user_by_user_name(user_name)

        # Шаг 2: Валидация пароля
        if not self._verify_password(password, user):
            return None

        # Шаг 3: Валидация пользователя
        if not self.auth_validator.validate_user_for_auth(user):
            return None

        # Шаг 4: Создание токенов
        return self._create_token_pair(user)

    def create_tokens(self, user: User) -> TokenPairDTO:
        """ Создание пары токенов """

        # Access токен
        access_token = self.jwt_service.create_access_token({
            "sub": str(auth_result.user_id),
            "username": auth_result.user_name,
            "role": auth_result.role.value
        })

        refresh_token = self.jwt_service.create_refresh_token({
            "sub": str(user.id)
        })

        # Refresh токен
        refresh_token = self.jwt_service.create_refresh_token({
            "sub": str(user.id)
        })

        # Сохранение refresh токена в БД (через репозиторий)
        refresh_data = self.mapper.to_refresh_token_data(
            user_id=auth_result.user_id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        )

        # TODO: Сохранить refresh токен через репозиторий
        # self.user_repo.save_refresh_token(refresh_data)

        return self.mapper.to_token_pair(access_token, refresh_token)

    def refresh_access_token(
        self,
        refresh_token: str
    ) -> Optional[TokenPairDTO]:
        """Обновление токенов"""

        valid_token = self.refresh_token_service.get_valid_token(refresh_token)
        if not valid_token:
            return None

        user = self.user_repo.get_user_by_id(valid_token.user_id)
        if not user:
            return None

        self.refresh_token_service.revoke_token(refresh_token)
        return self.create_tokens(user)
