"""
Usecase для блокировки пользователя
"""

from datetime import datetime, timedelta
from uuid import UUID

from ...schemas.requests import UserLockRequestDTO
from ...schemas.responses import UserLockResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException
from ....models.user_models import User


class LockUserUsecase(BaseUsecase):
    """Usecase для блокировки пользователя"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: UserLockRequestDTO
    ) -> UserLockResponseDTO:
        """Выполнение блокировки пользователя"""
        try:
            # Валидация UUID
            try:
                user_id = UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Получение пользователя
            user = await self.user_repository.get_by_id(str(user_id))
            if not user:
                raise NotFoundException("User not found")

            # Проверка, что пользователь не заблокирован
            if user.is_locked and user.locked_until and user.locked_until > datetime.utcnow():
                raise ValidationException("User is already locked")

            # Определение времени блокировки
            locked_until = None
            if request.duration_hours:
                locked_until = datetime.utcnow() + timedelta(hours=request.duration_hours)

            # Блокировка пользователя
            lock_data = {
                "is_locked": True,
                "locked_until": locked_until,
                "lock_reason": request.reason or "Locked by admin"
            }

            updated_user = await self.user_repository.update(str(user_id), lock_data)
            if not updated_user:
                raise ValidationException("Failed to lock user")

            # Возврат результата
            return UserLockResponseDTO.create_success(
                user_id=str(user_id),
                reason=request.reason,
                duration_hours=request.duration_hours
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to lock user: {str(e)}")
