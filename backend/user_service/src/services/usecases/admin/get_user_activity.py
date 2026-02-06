"""
Usecase для получения активности пользователя
"""


from uuid import UUID
from datetime import datetime, timedelta

from ...dto.requests import UserActivityRequestDTO
from ...dto.responses import UserActivityResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException


class GetUserActivityUsecase(BaseUsecase):
    """Usecase для получения активности пользователя"""

    def __init__(self, user_repository, activity_repository=None, **kwargs):
        self.user_repository = user_repository
        self.activity_repository = activity_repository  # Может быть None
        super().__init__(**kwargs)

    async def execute(self, request: UserActivityRequestDTO) -> UserActivityResponseDTO:
        """Выполнение получения активности пользователя"""
        try:
            # Валидация UUID
            try:
                UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Валидация количества дней
            if request.days < 1 or request.days > 365:
                raise ValidationException("Days must be between 1 and 365")

            # Получение пользователя
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise NotFoundException("User not found")

            # Вычисление даты начала периода
            start_date = datetime.utcnow() - timedelta(days=request.days)

            # Подготовка данных активности
            activity_data = {
                "user_id": str(request.user_id),
                "period_days": request.days,
                "period_start": start_date.isoformat(),
                "period_end": datetime.utcnow().isoformat(),
                "user_info": {
                    "email": user['email'],
                    "full_name": user.get('full_name') or f"{user.get('first_name', '')} {user.get('last_name', '')}",
                    "last_login_at": user['last_login_at'].isoformat() if user.get('last_login_at') else None,
                    "last_login_ip": user.get('last_login_ip')
                }
            }

            # Получение статистики входов (если есть репозиторий активности)
            if self.activity_repository:
                login_stats = await self.activity_repository.get_login_stats(
                    user_id=request.user_id,
                    start_date=start_date,
                    end_date=datetime.utcnow()
                )

                activity_data.update({
                    "login_statistics": {
                        "total_logins": login_stats.get('total_logins', 0),
                        "successful_logins": login_stats.get('successful_logins', 0),
                        "failed_logins": login_stats.get('failed_logins', 0),
                        "unique_ips": len(login_stats.get('unique_ips', [])),
                        "last_login_source": login_stats.get('last_login_source')
                    }
                })
            else:
                # Базовая статистика из данных пользователя
                activity_data.update({
                    "login_statistics": {
                        "total_logins": user.get('login_count', 0),
                        "successful_logins": user.get('login_count', 0),
                        "failed_logins": 0,
                        "unique_ips": 1 if user.get('last_login_ip') else 0,
                        "last_login_source": "web"  # По умолчанию
                    }
                })

            # Получение истории действий (если есть репозиторий активности)
            if self.activity_repository:
                recent_actions = await self.activity_repository.get_recent_actions(
                    user_id=request.user_id,
                    start_date=start_date,
                    limit=50
                )

                activity_data["recent_actions"] = [
                    {
                        "action": action['action'],
                        "timestamp": action['created_at'].isoformat(),
                        "ip_address": action.get('ip_address'),
                        "user_agent": action.get('user_agent')
                    }
                    for action in recent_actions
                ]
            else:
                activity_data["recent_actions"] = []

            # Возврат результата
            return UserActivityResponseDTO.create_success(activity_data)

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to get user activity: {str(e)}")
