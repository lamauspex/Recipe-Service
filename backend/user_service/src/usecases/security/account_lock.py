"""
Usecase для блокировки аккаунта пользователя
"""

from uuid import UUID

from ...schemas.requests import UserLockRequestDTO
from ...schemas.responses import UserLockResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException


class AccountLockUsecase(BaseUsecase):
    """Usecase для блокировки аккаунта пользователя"""

    def __init__(self, user_repository, security_service, **kwargs):
        self.user_repository = user_repository
        self.security_service = security_service
        super().__init__(**kwargs)

    async def execute(self, request: UserLockRequestDTO) -> UserLockResponseDTO:
        """Выполнение блокировки аккаунта"""
        try:
            # Валидация UUID
            try:
                UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Валидация причины блокировки
            if not request.reason or len(request.reason.strip()) < 3:
                raise ValidationException(
                    "Lock reason must be at least 3 characters long")

            # Валидация длительности блокировки
            # максимум год
            if request.duration_hours and (request.duration_hours < 1 or request.duration_hours > 8760):
                raise ValidationException(
                    "Duration must be between 1 and 8760 hours")

            # Получение пользователя
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise NotFoundException("User not found")

            # Проверка текущего статуса блокировки
            if getattr(user, 'is_locked', False) and getattr(user, 'locked_until', None):
                from datetime import datetime
                if user.locked_until > datetime.utcnow():
                    return UserLockResponseDTO(
                        success=False,
                        message="User is already locked",
                        data={
                            "user_id": request.user_id,
                            "already_locked": True,
                            "locked_until": user.locked_until.isoformat(),
                            "current_reason": getattr(user, 'lock_reason', None)
                        }
                    )

            # Блокировка аккаунта
            lock_result = await self.security_service.lock_user_account(
                user_id=request.user_id,
                reason=request.reason.strip(),
                duration_hours=request.duration_hours
            )

            if not lock_result:
                raise ValidationException("Failed to lock user account")

            # Получение обновленной информации о пользователе
            updated_user = await self.user_repository.get_by_id(request.user_id)

            # Возврат результата
            return UserLockResponseDTO.create_success(
                user_id=request.user_id,
                reason=request.reason.strip(),
                duration_hours=request.duration_hours
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to lock account: {str(e)}")


class AccountUnlockUsecase(BaseUsecase):
    """Usecase для разблокировки аккаунта пользователя"""

    def __init__(self, user_repository, security_service, **kwargs):
        self.user_repository = user_repository
        self.security_service = security_service
        super().__init__(**kwargs)

    async def execute(self, request: UserUnlockRequestDTO) -> UserUnlockResponseDTO:
        """Выполнение разблокировки аккаунта"""
        try:
            # Валидация UUID
            try:
                UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Получение пользователя
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise NotFoundException("User not found")

            # Проверка, что пользователь заблокирован
            if not getattr(user, 'is_locked', False):
                return UserUnlockResponseDTO(
                    success=True,
                    message="User account is not locked",
                    data={
                        "user_id": request.user_id,
                        "was_locked": False
                    }
                )

            # Разблокировка аккаунта
            unlock_result = await self.security_service.unlock_user_account(request.user_id)

            if not unlock_result:
                raise ValidationException("Failed to unlock user account")

            # Возврат результата
            return UserUnlockResponseDTO.create_success(
                user_id=request.user_id
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to unlock account: {str(e)}")
