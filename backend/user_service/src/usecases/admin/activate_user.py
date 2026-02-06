"""
Usecase для активации пользователя
Мигрирован из старой архитектуры
"""

from uuid import UUID
from datetime import datetime
from typing import Dict, Any

from ...schemas.requests import UserIdRequestDTO
from ...schemas.responses import UserResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import (
    NotFoundException,
    ValidationException
)


class ActivateUserUsecase(BaseUsecase):
    """Usecase для активации пользователя"""

    def __init__(self, user_repository, security_coordinator, **kwargs):
        self.user_repository = user_repository
        self.security_coordinator = security_coordinator
        super().__init__(**kwargs)

    async def execute(self, request: UserIdRequestDTO) -> UserResponseDTO:
        """Выполнение активации пользователя"""
        try:
            # Валидация UUID
            try:
                UUID(request.user_id)
            except ValueError:
                raise ValidationException("Некорректный формат user_id")

            # Получение пользователя
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise NotFoundException(
                    f"Пользователь с ID {request.user_id} не найден")

            # Проверяем, не активен ли уже пользователь
            if user.is_active:
                return UserResponseDTO.create_success(
                    UserResponseDTO.from_orm(user),
                    message="Пользователь уже активен"
                )

            # Активируем пользователя
            update_data = {
                "is_active": True,
                "updated_at": datetime.utcnow()
            }

            updated_user = await self.user_repository.update(request.user_id, update_data)

            # Сбрасываем флаги безопасности для пользователя
            if hasattr(self, 'security_coordinator') and self.security_coordinator:
                await self.security_coordinator.reset_security_flags(email=updated_user.email)

            return UserResponseDTO.create_success(
                UserResponseDTO.from_orm(updated_user),
                message=f"Пользователь {updated_user.email} успешно активирован"
            )

        except (NotFoundException, ValidationException) as e:
            raise e
        except Exception as e:
            raise ValidationException(
                f"Ошибка при активации пользователя: {str(e)}")
