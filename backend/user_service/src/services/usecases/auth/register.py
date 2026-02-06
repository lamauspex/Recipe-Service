"""
Usecase для регистрации пользователей
"""
from typing import Optional, Dict, Any
from ...dto.requests import RegisterRequestDTO
from ...dto.responses import RegisterResponseDTO, UserResponseDTO
from ..base import BaseUsecase, UsecaseResult
from ...infrastructure.common.exceptions import (
    ConflictException, 
    ValidationException
)


class RegisterUsecase(BaseUsecase):
    """Usecase для регистрации нового пользователя"""
    
    def __init__(
        self,
        user_repository,
        security_service,
        **kwargs
    ):
        self.user_repository = user_repository
        self.security_service = security_service
        super().__init__(**kwargs)
    
    async def execute(self, request: RegisterRequestDTO) -> RegisterResponseDTO:
        """Выполнение регистрации"""
        try:
            # Валидация входных данных
            if not request.email or not request.password:
                raise ValidationException("Email and password are required")
            
            if len(request.password) < 8:
                raise ValidationException("Password must be at least 8 characters long")
            
            if not request.first_name or not request.last_name:
                raise ValidationException("First name and last name are required")
            
            # Проверка уникальности email
            if await self.user_repository.exists_by_email(request.email):
                raise ConflictException("User with this email already exists")
            
            # Хеширование пароля
            hashed_password = await self.security_service.hash_password(request.password)
            
            # Создание пользователя
            user_data = {
                "email": request.email,
                "hashed_password": hashed_password,
                "first_name": request.first_name,
                "last_name": request.last_name,
                "phone": request.phone,
                "role": "user",
                "is_active": True,
                "is_verified": False
            }
            
            user = await self.user_repository.create(user_data)
            
            # Подготовка ответа
            user_response = UserResponseDTO(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
            return RegisterResponseDTO.create_success(user_response)
            
        except Exception as e:
            if isinstance(e, (ConflictException, ValidationException)):
                raise e
            raise ValidationException("Registration failed")