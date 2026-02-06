""" Usecase для логирования попытки входа """

from ...dto.requests.login_logging import LoginAttemptLogRequestDTO
from ...dto.responses.login_monitoring import LoginAttemptLogResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ValidationException


class LogLoginAttemptUsecase(BaseUsecase):
    """Usecase для логирования попытки входа"""

    def __init__(
        self,
        login_log_repository,
        user_repository,  # для обновления данных пользователя
        **kwargs
    ):
        self.login_log_repository = login_log_repository
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: LoginAttemptLogRequestDTO
    ) -> LoginAttemptLogResponseDTO:
        """Выполнение логирования попытки входа"""

        # Валидация входных данных
        if not request.email or not request.ip_address:
            raise ValidationException("Email and IP address are required")

        # Поиск пользователя для обновления его данных
        user = await self.user_repository.get_by_email(request.email)
        user_id = user.id if user else None

        # Логирование попытки входа
        log_data = await self.login_log_repository.log_login_attempt(
            email=request.email,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            success=request.success,
            failure_reason=request.failure_reason,
            user_id=user_id
        )

        # Обновление данных пользователя (если найден)
        if user and request.success:
            await self.user_repository.update(user.id, {
                "last_login_at": request.timestamp,
                "last_login_ip": request.ip_address,
                "last_user_agent": request.user_agent
            })

        return LoginAttemptLogResponseDTO.create_success(log_data)
