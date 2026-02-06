"""
Интерфейсы для сервисов аутентификации и авторизации
"""
from abc import ABC, abstractmethod
from typing import Optional
from ..dto.requests import (
    LoginRequestDTO, 
    RegisterRequestDTO, 
    RefreshTokenRequestDTO,
    LogoutRequestDTO,
    PasswordResetRequestDTO,
    PasswordResetConfirmRequestDTO
)
from ..dto.responses import (
    LoginResponseDTO, 
    RegisterResponseDTO, 
    TokenRefreshResponseDTO,
    LogoutResponseDTO,
    PasswordResetResponseDTO
)


class AuthInterface(ABC):
    """Интерфейс сервиса аутентификации"""
    
    @abstractmethod
    async def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        """Авторизация пользователя"""
        pass
    
    @abstractmethod
    async def register(self, request: RegisterRequestDTO) -> RegisterResponseDTO:
        """Регистрация нового пользователя"""
        pass
    
    @abstractmethod
    async def refresh_token(self, request: RefreshTokenRequestDTO) -> TokenRefreshResponseDTO:
        """Обновление access токена"""
        pass
    
    @abstractmethod
    async def logout(self, request: LogoutRequestDTO) -> LogoutResponseDTO:
        """Выход пользователя"""
        pass
    
    @abstractmethod
    async def request_password_reset(self, request: PasswordResetRequestDTO) -> PasswordResetResponseDTO:
        """Запрос сброса пароля"""
        pass
    
    @abstractmethod
    async def confirm_password_reset(self, request: PasswordResetConfirmRequestDTO) -> PasswordResetResponseDTO:
        """Подтверждение сброса пароля"""
        pass