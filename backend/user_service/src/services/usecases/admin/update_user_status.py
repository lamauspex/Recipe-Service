"""
Usecase для обновления статуса пользователя
"""


from uuid import UUID

from ...dto.requests import UserStatusUpdateRequestDTO
from ...dto.responses import UserStatusResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException


class UpdateUserStatusUsecase(BaseUsecase):
    """Usecase для обновления статуса пользователя"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: UserStatusUpdateRequestDTO
    ) -> UserStatusResponseDTO:
        """Выполнение обновления статуса пользователя"""
        try:
            # Валидация UUID
            try:
                UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Валидация статуса
            valid_statuses = ['activate', 'deactivate', 'lock', 'unlock']
            if request.status not in valid_statuses:
                raise ValidationException(
                    f"Invalid status. Must be one of: {valid_statuses}")

            # Получение пользователя
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise NotFoundException("User not found")

            # Определение действий по статусу
            update_data = {}
            audit_data = {
                'action': request.status,
                'reason': request.reason,
                'performed_by': 'admin'  # Из контекста аутентификации
            }

            if request.status == 'activate':
                update_data = {
                    'is_active': True,
                    'is_locked': False,
                    'locked_until': None,
                    'lock_reason': None
                }
                audit_data['description'] = 'User activated by admin'

            elif request.status == 'deactivate':
                update_data = {
                    'is_active': False,
                    'is_locked': True,
                    'locked_until': None,
                    'lock_reason': 'Deactivated by admin'
                }
                audit_data['description'] = 'User deactivated by admin'

            elif request.status == 'lock':
                update_data = {
                    'is_locked': True,
                    'locked_until': None,  # Можно добавить время блокировки
                    'lock_reason': request.reason or 'Locked by admin'
                }
                audit_data['description'] = f'User locked by admin: {request.reason or "No reason provided"}'

            elif request.status == 'unlock':
                update_data = {
                    'is_locked': False,
                    'locked_until': None,
                    'lock_reason': None
                }
                audit_data['description'] = 'User unlocked by admin'

            # Обновление пользователя
            updated_user = await self.user_repository.update(request.user_id, update_data)

            if not updated_user:
                raise ValidationException("Failed to update user status")

            # Создание записи в аудите (если есть такой репозиторий)
            # await self.audit_repository.create(audit_data)

            # Возврат результата
            return UserStatusResponseDTO.create_success(
                user_id=str(request.user_id),
                status=request.status
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(
                f"Failed to update user status: {str(e)}")
