""" Сервис для мониторинга и логирования входов """


from backend.user_service.src.services.dto.requests.login_logging import (
    LoginAttemptLogRequestDTO,
    LoginHistoryRequestDTO,
    LoginStatisticsRequestDTO)
from backend.user_service.src.services.dto.responses.login_monitoring import (
    LoginAttemptLogResponseDTO,
    LoginHistoryResponseDTO,
    LoginStatisticsResponseDTO)
from ...interfaces.admin import AdminInterface


class LoginMonitoringService(AdminInterface):
    """Сервис для мониторинга и логирования входов"""

    def __init__(
        self,
        log_login_attempt_usecase,
        get_login_history_usecase,
        get_login_statistics_usecase,
        get_failed_login_attempts_usecase,
        get_suspicious_activity_usecase
    ):
        self.log_login_attempt_usecase = log_login_attempt_usecase
        self.get_login_history_usecase = get_login_history_usecase
        self.get_login_statistics_usecase = get_login_statistics_usecase
        self.get_failed_login_attempts_usecase = get_failed_login_attempts_usecase
        self.get_suspicious_activity_usecase = get_suspicious_activity_usecase

    async def log_login_attempt(
        self,
        request: LoginAttemptLogRequestDTO
    ) -> LoginAttemptLogResponseDTO:
        """Логирование попытки входа"""
        return await self.log_login_attempt_usecase.execute(request)

    async def get_login_history(
        self,
        request: LoginHistoryRequestDTO
    ) -> LoginHistoryResponseDTO:
        """Получение истории входов"""
        return await self.get_login_history_usecase.execute(request)

    async def get_login_statistics(
        self,
        request: LoginStatisticsRequestDTO
    ) -> LoginStatisticsResponseDTO:
        """Получение статистики входов"""
        return await self.get_login_statistics_usecase.execute(request)

    async def get_failed_login_attempts(
        self,
        request: LoginStatisticsRequestDTO
    ) -> LoginAttemptLogResponseDTO:
        """Получение неудачных попыток входа"""
        return await self.get_failed_login_attempts_usecase.execute(request)

    async def get_suspicious_activity(
        self,
        request: LoginStatisticsRequestDTO
    ) -> LoginStatisticsResponseDTO:
        """Получение подозрительной активности"""
        return await self.get_suspicious_activity_usecase.execute(request)
