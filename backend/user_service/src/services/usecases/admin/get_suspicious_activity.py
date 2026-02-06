"""
Usecase для получения подозрительной активности
"""

from typing import Dict, Any, List
from datetime import datetime

from ...dto.requests import UserActivityRequestDTO
from ...dto.responses import UserActivityResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ValidationException, NotFoundException


class GetSuspiciousActivityUsecase(BaseUsecase):
    """Usecase для получения подозрительной активности"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: UserActivityRequestDTO) -> UserActivityResponseDTO:
        """Выполнение получения подозрительной активности"""
        try:
            # Валидация UUID
            try:
                UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Валидация дней
            if request.days < 1 or request.days > 90:
                raise ValidationException("Days must be between 1 and 90")

            # Получение пользователя
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise NotFoundException("User not found")

            # Получение подозрительной активности
            suspicious_activity = await self.user_repository.get_suspicious_activity(
                limit=100
            )

            # Форматирование результатов
            formatted_activity = []
            for activity in suspicious_activity:
                formatted_entry = {
                    "timestamp": activity.get('timestamp', '').isoformat() if activity.get('timestamp') else '',
                    "type": activity.get('type', 'unknown'),
                    "description": activity.get('description', ''),
                    "ip_address": activity.get('ip_address', ''),
                    "user_agent": activity.get('user_agent', ''),
                    "severity": activity.get('severity', 'low'),
                    "details": activity.get('details', {})
                }
                formatted_activity.append(formatted_entry)

            # Возврат результата
            return UserActivityResponseDTO.create_success({
                "user_id": str(request.user_id),
                "email": user.email,
                "suspicious_activity": formatted_activity,
                "total_suspicious_events": len(formatted_activity),
                "high_severity_count": len([a for a in formatted_activity if a.get('severity') == 'high']),
                "period_days": request.days,
                "generated_at": datetime.utcnow().isoformat()
            })

        except Exception as e:
            if isinstance(e, (ValidationException, NotFoundException)):
                raise e
            raise ValidationException(
                f"Failed to get suspicious activity: {str(e)}")
