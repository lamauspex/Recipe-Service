"""
Основной сервис аутентификации
"""


from ...interfaces.auth import AuthInterface
from ...schemas.requests import (
    LoginRequestDTO,
    RegisterRequestDTO,
    RefreshTokenRequestDTO,
    LogoutRequestDTO,
    PasswordResetRequestDTO,
    PasswordResetConfirmRequestDTO
)
from ...schemas.responses import (
    LoginResponseDTO,
    RegisterResponseDTO,
    TokenRefreshResponseDTO,
    LogoutResponseDTO,
    PasswordResetResponseDTO
)


class AuthService(AuthInterface):
    """Основной сервис аутентификации"""

    def __init__(
        self,
        login_usecase,
        register_usecase,
        refresh_token_usecase,
        logout_usecase,
        password_reset_usecase,
        password_reset_confirm_usecase
    ):
        self.login_usecase = login_usecase
        self.register_usecase = register_usecase
        self.refresh_token_usecase = refresh_token_usecase
        self.logout_usecase = logout_usecase
        self.password_reset_usecase = password_reset_usecase
        self.password_reset_confirm_usecase = password_reset_confirm_usecase

    async def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        """Авторизация пользователя"""
        return await self.login_usecase.execute(request)

    async def register(self, request: RegisterRequestDTO) -> RegisterResponseDTO:
        """Регистрация нового пользователя"""
        return await self.register_usecase.execute(request)

    async def refresh_token(self, request: RefreshTokenRequestDTO) -> TokenRefreshResponseDTO:
        """Обновление access токена"""
        return await self.refresh_token_usecase.execute(request)

    async def logout(self, request: LogoutRequestDTO) -> LogoutResponseDTO:
        """Выход пользователя"""
        return await self.logout_usecase.execute(request)

    async def request_password_reset(self, request: PasswordResetRequestDTO) -> PasswordResetResponseDTO:
        """Запрос сброса пароля"""
        # Заглушка - реализуем позже
        return PasswordResetResponseDTO(message="Password reset instructions sent to your email")

    async def confirm_password_reset(self, request: PasswordResetConfirmRequestDTO) -> PasswordResetResponseDTO:
        """Подтверждение сброса пароля"""
        # Заглушка - реализуем позже
        return PasswordResetResponseDTO(message="Password has been reset successfully")
