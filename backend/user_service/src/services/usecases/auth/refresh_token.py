"""
Usecase для обновления токенов
"""
from typing import Optional, Dict, Any
from ...dto.requests import RefreshTokenRequestDTO
from ...dto.responses import TokenRefreshResponseDTO, AuthTokensDTO
from ..base import BaseUsecase, UsecaseResult
from ...infrastructure.common.exceptions import (
    UnauthorizedException,
    ValidationException
)


class RefreshTokenUsecase(BaseUsecase):
    """Usecase для обновления access токена"""

    def __init__(
        self,
        token_repository,
        security_service,
        user_repository,
        **kwargs
    ):
        self.token_repository = token_repository
        self.security_service = security_service
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: RefreshTokenRequestDTO) -> TokenRefreshResponseDTO:
        """Выполнение обновления токена"""
        try:
            # Валидация входных данных
            if not request.refresh_token:
                raise ValidationException("Refresh token is required")

            # Проверка refresh токена
            token_data = await self.security_service.verify_refresh_token(request.refresh_token)
            if not token_data:
                raise UnauthorizedException("Invalid refresh token")

            # Поиск токена в базе данных
            token_record = await self.token_repository.get_by_token(request.refresh_token)
            if not token_record or token_record.is_revoked:
                raise UnauthorizedException("Refresh token is revoked")

            # Проверка истечения токена
            from datetime import datetime
            if token_record.expires_at < datetime.utcnow():
                await self.token_repository.revoke_by_token(request.refresh_token)
                raise UnauthorizedException("Refresh token has expired")

            # Получение пользователя
            user = await self.user_repository.get_by_id(token_data["user_id"])
            if not user or not user.is_active:
                raise UnauthorizedException("User not found or deactivated")

            # Генерация новых токенов
            user_data = {
                "user_id": user.id,
                "email": user.email,
                "role": user.role
            }

            access_token = await self.security_service.generate_access_token(user_data)
            new_refresh_token = await self.security_service.generate_refresh_token(user_data)

            # Отзыв старого refresh токена
            await self.token_repository.revoke_by_token(request.refresh_token)

            # Сохранение нового refresh токена
            await self.token_repository.create({
                "user_id": user.id,
                "token": new_refresh_token,
                "token_type": "refresh",
                "expires_at": self._get_refresh_token_expiry(),
                "is_revoked": False
            })

            # Подготовка ответа
            tokens = AuthTokensDTO(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=3600,  # 1 час
                token_type="Bearer"
            )

            return TokenRefreshResponseDTO.create_success(tokens)

        except Exception as e:
            if isinstance(e, (UnauthorizedException, ValidationException)):
                raise e
            raise UnauthorizedException("Token refresh failed")

    def _get_refresh_token_expiry(self):
        """Получение даты истечения refresh токена"""
        from datetime import datetime, timedelta
        return datetime.utcnow() + timedelta(days=30)
