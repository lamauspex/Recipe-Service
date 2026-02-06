"""
Usecase для получения истории входов пользователей
"""

from datetime import datetime
from uuid import UUID

from ...schemas.requests import UserActivityRequestDTO
from ...schemas.responses import UserActivityResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import (
    ValidationException,
    NotFoundException
)


class GetLoginHistoryUsecase(BaseUsecase):
    """Usecase для получения истории входов пользователя"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: UserActivityRequestDTO) -> UserActivityResponseDTO:
        """Выполнение получения истории входов"""
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

            # Получение истории входов
            login_history = await self.user_repository.get_login_history(
                request.user_id, limit=100
            )

            # Форматирование результатов
            formatted_history = []
            for entry in login_history:
                formatted_entry = {
                    "timestamp": entry.get('timestamp', '').isoformat() if entry.get('timestamp') else '',
                    "ip_address": entry.get('ip_address', ''),
                    "user_agent": entry.get('user_agent', ''),
                    "success": entry.get('success', False),
                    "failure_reason": entry.get('failure_reason', None)
                }
                formatted_history.append(formatted_entry)

            # Возврат результата
            return UserActivityResponseDTO.create_success({
                "user_id": str(request.user_id),
                "email": user.email,
                "login_history": formatted_history,
                "total_login_attempts": len(formatted_history),
                "successful_logins": len([h for h in formatted_history if h['success']]),
                "failed_logins": len([h for h in formatted_history if not h['success']]),
                "period_days": request.days,
                "account_created": user.created_at.isoformat() if user.created_at else None
            })

        except Exception as e:
            if isinstance(e, (ValidationException, NotFoundException)):
                raise e
            raise ValidationException(f"Failed to get login history: {str(e)}")
