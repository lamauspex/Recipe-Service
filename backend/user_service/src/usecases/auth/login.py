"""
Usecase для авторизации пользователей
"""


from ...schemas.requests import LoginRequestDTO
from ...schemas.responses import LoginResponseDTO, UserResponseDTO, AuthTokensDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import (
    UnauthorizedException,
    ValidationException
)


class LoginUsecase(BaseUsecase):
    """Usecase для авторизации пользователя"""

    def __init__(
        self,
        user_repository,
        security_service,
        token_repository,
        **kwargs
    ):
        self.user_repository = user_repository
        self.security_service = security_service
        self.token_repository = token_repository
        super().__init__(**kwargs)

    async def execute(self, request: LoginRequestDTO) -> LoginResponseDTO:
        """Выполнение авторизации"""
        try:
            # Валидация входных данных
            if not request.email or not request.password:
                raise ValidationException("Email and password are required")

            # Поиск пользователя
            user = await self.user_repository.get_by_email(request.email)
            if not user:
                raise UnauthorizedException("Invalid email or password")

            # Проверка активности пользователя
            if not user.is_active:
                raise UnauthorizedException("User account is deactivated")

            # Проверка пароля
            is_valid_password = await self.security_service.verify_password(
                request.password,
                user.hashed_password
            )
            if not is_valid_password:
                raise UnauthorizedException("Invalid email or password")

            # Генерация токенов
            user_data = {
                "user_id": user.id,
                "email": user.email,
                "role": user.role
            }

            access_token = await self.security_service.generate_access_token(user_data)
            refresh_token = await self.security_service.generate_refresh_token(user_data)

            # Сохранение refresh токена
            await self.token_repository.create({
                "user_id": user.id,
                "token": refresh_token,
                "token_type": "refresh",
                "expires_at": self._get_refresh_token_expiry(),
                "is_revoked": False
            })

            # Подготовка ответа
            user_response = UserResponseDTO(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            )

            tokens = AuthTokensDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=3600,  # 1 час
                token_type="Bearer"
            )

            return LoginResponseDTO.create_success(user_response, tokens)

        except Exception as e:
            if isinstance(e, (UnauthorizedException, ValidationException)):
                raise e
            raise UnauthorizedException("Login failed")

    def _get_refresh_token_expiry(self):
        """Получение даты истечения refresh токена"""
        from datetime import datetime, timedelta
        return datetime.utcnow() + timedelta(days=30)
