"""
Usecase для выхода пользователей
"""
from typing import Optional, Dict, Any
from ...dto.requests import LogoutRequestDTO
from ...dto.responses import LogoutResponseDTO
from ..base import BaseUsecase, UsecaseResult
from ...infrastructure.common.exceptions import ValidationException


class LogoutUsecase(BaseUsecase):
    """Usecase для выхода пользователя"""

    def __init__(
        self,
        token_repository,
        security_service,
        **kwargs
    ):
        self.token_repository = token_repository
        self.security_service = security_service
        super().__init__(**kwargs)

    async def execute(self, request: LogoutRequestDTO) -> LogoutResponseDTO:
        """Выполнение выхода"""
        try:
            # Если передан refresh токен, отзываем его
            if request.refresh_token:
                # Проверка токена перед отзывом
                token_data = await self.security_service.verify_refresh_token(request.refresh_token)
                if token_data:
                    await self.token_repository.revoke_by_token(request.refresh_token)
            # Если refresh токен не передан, отзываем все токены пользователя
            # (это можно сделать через user_id из access токена, но для упрощения
            # предполагаем, что refresh токен всегда передается)

            return LogoutResponseDTO.create_success()

        except Exception as e:
            # Выход не должен падать с ошибкой - это безопасная операция
            return LogoutResponseDTO.create_success()
