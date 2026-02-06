"""Usecase для логирования попытки входа"""

from typing import Dict, Any
from datetime import datetime

from ...schemas.requests import BaseRequestDTO
from ...schemas.responses import BaseResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ValidationException
from ....models.user_models import User


class LogLoginAttemptUsecase(BaseUsecase):
    """Usecase для логирования попытки входа"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: BaseRequestDTO) -> BaseResponseDTO:
        """Выполнение логирования попытки входа"""
        try:
            # Валидация входных данных
            if not hasattr(request, 'email') or not request.email:
                raise ValidationException("Email is required")

            if not hasattr(request, 'ip_address') or not request.ip_address:
                raise ValidationException("IP address is required")

            # Поиск пользователя для обновления его данных
            user = await self.user_repository.get_by_email(request.email)
            user_id = str(user.id) if user else None

            # Подготовка данных для логирования
            log_data = {
                "email": request.email,
                "ip_address": request.ip_address,
                "user_agent": getattr(request, 'user_agent', None),
                "success": getattr(request, 'success', False),
                "failure_reason": getattr(request, 'failure_reason', None),
                "user_id": user_id,
                "timestamp": getattr(request, 'timestamp', datetime.utcnow())
            }

            # Обновление данных пользователя (если найден)
            if user and request.success:
                update_data = {
                    "last_login": datetime.utcnow(),
                    "login_count": user.login_count + 1
                }
                await self.user_repository.update(str(user.id), update_data)

            # Возврат результата
            return BaseResponseDTO(
                success=True,
                message="Login attempt logged successfully",
                data=log_data
            )

        except Exception as e:
            if isinstance(e, ValidationException):
                raise e
            raise ValidationException(f"Failed to log login attempt: {str(e)}")
