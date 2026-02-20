"""
Координирующий слой, который вызывает методы остальных служб
для выполнения необходимых операций
"""

from datetime import datetime, timedelta, timezone
from typing import Optional


from backend.user_service.src.protocols.token_repository import TokenRepositoryProtocol
from backend.user_service.src.schemas.auth.auth_dto import TokenPairDTO
from backend.shared.models import User
from backend.user_service.src.config import (
    ApiConfig,
    AuthConfig
)
from backend.user_service.src.core import (
    PasswordService,
    JWTService,
    AuthValidator
)
from backend.user_service.src.protocols import (
    UserRepositoryProtocol
)
from backend.user_service.src.service.auth_service.mappers import AuthMapper


class AuthService:
    """ Сервис аутентификации """

    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        password_service: PasswordService,
        jwt_service: JWTService,
        auth_config: AuthConfig,
        api_config: ApiConfig,
        auth_validator: AuthValidator,
        mapper: AuthMapper,
        token_repo: TokenRepositoryProtocol
    ):
        self.user_repo = user_repo
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.auth_config = auth_config
        self.api_config = api_config
        self.auth_validator = auth_validator
        self.mapper = mapper
        self.token_repo = token_repo

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
        return self.create_tokens(user)

    def _verify_password(
        self,
        password: str,
        user: Optional[User]
    ) -> bool:
        """Проверка пароля"""

        if not user:
            return False
        return self.password_service.verify_password(
            password,
            user.hashed_password
        )

    def create_tokens(self, user: User) -> TokenPairDTO:
        """Создание пары токенов"""

        # Access токен
        access_token = self.jwt_service.create_access_token({
            "sub": str(user.id),
            "username": user.user_name,
            "role": user.primary_role.value if user.primary_role else "user"
        })

        # Refresh токен
        refresh_token = self.jwt_service.create_refresh_token({
            "sub": str(user.id)
        })

        # Подготовка данных для сохранения refresh токена
        refresh_data = self.mapper.to_refresh_token_data(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(
                days=self.auth_config.REFRESH_TOKEN_EXPIRE_DAYS
            )
        )

        self.token_repo.create_refresh_token(refresh_data)

        return self.mapper.to_token_pair(
            access_token,
            refresh_token
        )

    def refresh_access_token(
        self,
        refresh_token: str
    ) -> Optional[TokenPairDTO]:
        """Обновление токенов"""

        valid_token = self.refresh_token_service.get_valid_token(
            refresh_token
        )
        if not valid_token:
            return None

        user = self.user_repo.get_user_by_id(valid_token.user_id)
        if not user:
            return None

        self.refresh_token_service.revoke_token(refresh_token)
        return self.create_tokens(user)
