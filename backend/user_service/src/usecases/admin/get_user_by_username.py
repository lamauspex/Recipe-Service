"""
Usecase для получения пользователя по username
Мигрирован из старой архитектуры
"""

from uuid import UUID
from typing import Dict, Any

from ...schemas.requests import UsernameRequestDTO
from ...schemas.responses import UserResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import (
    NotFoundException,
    ValidationException
)


class GetUserByUsernameUsecase(BaseUsecase):
    """Usecase для получения пользователя по username"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: UsernameRequestDTO) -> UserResponseDTO:
        """Выполнение поиска пользователя по username"""
        try:
            # Валидация username
            if not request.username or len(request.username.strip()) < 3:
                raise ValidationException(
                    "Username должен содержать минимум 3 символа")

            username = request.username.strip().lower()

            # Поиск пользователя по username
            user = await self.user_repository.get_by_username(username)
            if not user:
                raise NotFoundException(
                    f"Пользователь с username '{username}' не найден")

            # Подготовка ответа
            user_response = UserResponseDTO(
                id=user.id,
                email=user.email,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            )

            return UserResponseDTO.create_success(user_response)

        except (NotFoundException, ValidationException) as e:
            raise e
        except Exception as e:
            raise ValidationException(
                f"Ошибка при поиске пользователя: {str(e)}")
