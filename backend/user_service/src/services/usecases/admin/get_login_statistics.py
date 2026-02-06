"""
Usecase для получения статистики входов
"""
from typing import Dict, Any
from datetime import datetime
from uuid import UUID

from ...dto.requests import UserActivityRequestDTO
from ...dto.responses import UserActivityResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ValidationException, NotFoundException


class GetLoginStatisticsUsecase(BaseUsecase):
    """Usecase для получения статистики входов"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: UserActivityRequestDTO) -> UserActivityResponseDTO:
        """Выполнение получения статистики входов"""
        try:
            # Валидация UUID
            try:
                UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Валидация дней
            if request.days < 1 or request.days > 365:
                raise ValidationException("Days must be between 1 and 365")

            # Получение пользователя
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise NotFoundException("User not found")

            # Получение статистики входов
            statistics = await self.user_repository.get_login_statistics(
                request.user_id, days=request.days
            )

            # Возврат результата
            return UserActivityResponseDTO.create_success({
                "user_id": str(request.user_id),
                "email": user.email,
                "login_statistics": statistics,
                "period_days": request.days,
                "generated_at": datetime.utcnow().isoformat()
            })

        except Exception as e:
            if isinstance(e, (ValidationException, NotFoundException)):
                raise e
            raise ValidationException(
                f"Failed to get login statistics: {str(e)}")
