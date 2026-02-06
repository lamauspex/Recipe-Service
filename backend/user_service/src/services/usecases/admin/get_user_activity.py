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

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
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
                    "email": user.email,
                    "full_name": getattr(user, 'full_name', f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}"),
                    "last_login_at": user.last_login.isoformat() if user.last_login else None,
                    "last_login_ip": getattr(user, 'last_login_ip', None)
                }
            }

            # Получение статистики входов
            login_stats = await self.user_repository.get_login_statistics(
                request.user_id, days=request.days
            )

            activity_data.update({
                "login_statistics": login_stats
            })

            # Возврат результата
            return UserActivityResponseDTO.create_success(activity_data)

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to get user activity: {str(e)}")
