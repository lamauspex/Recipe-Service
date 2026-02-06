"""
Usecase для деактивации пользователя
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


class DeactivateUserUsecase(BaseUsecase):
    """Usecase для деактивации пользователя"""

    def __init__(self, user_repository, security_coordinator, **kwargs):
        self.user_repository = user_repository
        self.security_coordinator = security_coordinator
        super().__init__(**kwargs)

    async def execute(self, request: UserIdRequestDTO) -> UserResponseDTO:
        """Выполнение деактивации пользователя"""
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

            # Проверяем, не деактивирован ли уже пользователь
            if not user.is_active:
                return UserResponseDTO.create_success(
                    UserResponseDTO.from_orm(user),
                    message="Пользователь уже деактивирован"
                )

            # Деактивируем пользователя
            update_data = {
                "is_active": False,
                "updated_at": datetime.utcnow()
            }

            updated_user = await self.user_repository.update(request.user_id, update_data)

            # Блокируем аккаунт пользователя
            if hasattr(self, 'security_coordinator') and self.security_coordinator:
                await self.security_coordinator.account_locker.lock_account(
                    email=updated_user.email,
                    duration_minutes=525600,  # 1 год в минутах
                    reason="Аккаунт деактивирован администратором"
                )

            return UserResponseDTO.create_success(
                UserResponseDTO.from_orm(updated_user),
                message=f"Пользователь {updated_user.email} успешно деактивирован"
            )

        except (NotFoundException, ValidationException) as e:
            raise e
        except Exception as e:
            raise ValidationException(
                f"Ошибка при деактивации пользователя: {str(e)}")
