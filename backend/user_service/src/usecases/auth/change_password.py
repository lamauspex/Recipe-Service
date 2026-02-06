"""
Usecase для смены пароля пользователя
"""

from uuid import UUID

from ...schemas.requests import UserChangePasswordRequestDTO
from ...schemas.responses import BaseResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException, UnauthorizedException
from ...infrastructure.common.password_utility import password_utility


class ChangePasswordUsecase(BaseUsecase):
    """Usecase для смены пароля пользователя"""

    def __init__(self, user_repository, security_service, **kwargs):
        self.user_repository = user_repository
        self.security_service = security_service
        super().__init__(**kwargs)

    async def execute(
        self,
        request: UserChangePasswordRequestDTO
    ) -> BaseResponseDTO:
        """Выполнение смены пароля"""
        try:
            # Валидация пароля
            if not request.current_password or not request.new_password:
                raise ValidationException(
                    "Current password and new password are required")

            # Валидация сложности нового пароля
            is_strong, strength_msg = self.security_service.validate_password_strength(
                request.new_password)
            if not is_strong:
                raise ValidationException(
                    f"New password is too weak: {strength_msg}")

            # Получение пользователя (заглушка - в реальной реализации из токена)
            user_id = getattr(request, 'user_id', None)
            if not user_id:
                raise UnauthorizedException("User authentication required")

            # Получение пользователя
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise NotFoundException("User not found")

            # Проверка текущего пароля
            if not self.security_service.verify_password(request.current_password, user.hashed_password):
                raise UnauthorizedException("Current password is incorrect")

            # Хеширование нового пароля
            new_hashed_password = self.security_service.hash_password(
                request.new_password)

            # Обновление пароля
            update_data = {
                "hashed_password": new_hashed_password,
                "updated_at": self._get_current_timestamp()
            }

            updated_user = await self.user_repository.update(str(user_id), update_data)
            if not updated_user:
                raise ValidationException("Failed to update password")

            # Возврат результата
            return BaseResponseDTO(
                success=True,
                message="Password changed successfully"
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException, UnauthorizedException)):
                raise e
            raise ValidationException(f"Failed to change password: {str(e)}")
