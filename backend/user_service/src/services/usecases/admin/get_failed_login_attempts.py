"""
Usecase для получения неудачных попыток входа
"""

from typing import Dict, Any, List
from uuid import UUID

from ...dto.requests import UserActivityRequestDTO
from ...dto.responses import UserActivityResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ValidationException, NotFoundException


class GetFailedLoginAttemptsUsecase(BaseUsecase):
    """Usecase для получения неудачных попыток входа"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: UserActivityRequestDTO) -> UserActivityResponseDTO:
        """Выполнение получения неудачных попыток входа"""
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

            # Получение неудачных попыток входа
            failed_attempts = await self.user_repository.get_failed_login_attempts(
                request.user_id, limit=100
            )

            # Форматирование результатов
            formatted_attempts = []
            for attempt in failed_attempts:
                formatted_attempt = {
                    "timestamp": attempt.get('timestamp', '').isoformat() if attempt.get('timestamp') else '',
                    "ip_address": attempt.get('ip_address', ''),
                    "user_agent": attempt.get('user_agent', ''),
                    "failure_reason": attempt.get('failure_reason', 'Unknown error')
                }
                formatted_attempts.append(formatted_attempt)

            # Возврат результата
            return UserActivityResponseDTO.create_success({
                "user_id": str(request.user_id),
                "failed_login_attempts": formatted_attempts,
                "total_failed_attempts": len(formatted_attempts),
                "period_days": request.days
            })

        except Exception as e:
            if isinstance(e, (ValidationException, NotFoundException)):
                raise e
            raise ValidationException(
                f"Failed to get failed login attempts: {str(e)}")
