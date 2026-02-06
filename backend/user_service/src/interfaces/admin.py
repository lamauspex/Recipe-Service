"""
Интерфейсы для административных сервисов
"""
from abc import ABC, abstractmethod
from typing import List

from backend.user_service.src.schemas.requests.login_logging import (
    LoginAttemptLogRequestDTO,
    LoginHistoryRequestDTO,
    LoginStatisticsRequestDTO
)
from backend.user_service.src.schemas.requests import (
    UserListRequestDTO,
    UserStatusUpdateRequestDTO,
    UserDeleteRequestDTO,
    UserActivityRequestDTO,
    UserSearchRequestDTO
)
from backend.user_service.src.schemas.responses import (
    UserListResponseDTO,
    UserDetailResponseDTO,
    UserStatusResponseDTO,
    UserDeleteResponseDTO,
    UserActivityResponseDTO,
    UserSearchResponseDTO,
    FailedLoginAttemptsResponseDTO
)
from backend.user_service.src.schemas.responses.login_monitoring import (
    LoginAttemptLogResponseDTO,
    LoginHistoryResponseDTO,
    LoginStatisticsResponseDTO
)


class AdminInterface(ABC):
    """Интерфейс административного сервиса"""

    @abstractmethod
    async def get_user_statistics(self) -> dict:
        """Получение статистики пользователей"""
        pass

    @abstractmethod
    async def bulk_activate_users(self, user_ids: List[int]) -> dict:
        """Массовая активация пользователей"""
        pass

    @abstractmethod
    async def bulk_deactivate_users(self, user_ids: List[int]) -> dict:
        """Массовая деактивация пользователей"""
        pass

    @abstractmethod
    async def bulk_delete_users(self, user_ids: List[int]) -> dict:
        """Массовое удаление пользователей"""
        pass

    @abstractmethod
    async def export_users(self, format: str = "csv") -> bytes:
        """Экспорт пользователей"""
        pass

    @abstractmethod
    async def get_system_health(self) -> dict:
        """Получение состояния системы"""
        pass

    @abstractmethod
    async def log_login_attempt(
        self,
        request: LoginAttemptLogRequestDTO
    ) -> LoginAttemptLogResponseDTO:
        """Логирование попытки входа"""
        pass

    @abstractmethod
    async def get_login_history(
        self,
        request: LoginHistoryRequestDTO
    ) -> LoginHistoryResponseDTO:
        """Получение истории входов"""
        pass

    @abstractmethod
    async def get_login_statistics(
        self,
        request: LoginStatisticsRequestDTO
    ) -> LoginStatisticsResponseDTO:
        """Получение статистики входов"""
        pass

    @abstractmethod
    async def get_failed_login_attempts(
        self,
        request: LoginStatisticsRequestDTO
    ) -> FailedLoginAttemptsResponseDTO:
        """Получение неудачных попыток входа"""
        pass

    @abstractmethod
    async def get_suspicious_activity(
        self,
        request: LoginStatisticsRequestDTO
    ) -> LoginStatisticsResponseDTO:
        """Получение подозрительной активности"""
        pass


class UserManagementInterface(ABC):
    """Интерфейс для управления пользователями"""

    @abstractmethod
    async def get_users(
        self,
        request: UserListRequestDTO
    ) -> UserListResponseDTO:
        """Получение списка пользователей с фильтрацией"""
        pass

    @abstractmethod
    async def get_user_by_id(
        self,
        user_id: str
    ) -> UserDetailResponseDTO:
        """Получение пользователя по ID"""
        pass

    @abstractmethod
    async def update_user_status(
        self,
        request: UserStatusUpdateRequestDTO
    ) -> UserStatusResponseDTO:
        """Обновление статуса пользователя"""
        pass

    @abstractmethod
    async def delete_user(
        self,
        request: UserDeleteRequestDTO
    ) -> UserDeleteResponseDTO:
        """Удаление пользователя (мягкое удаление)"""
        pass

    @abstractmethod
    async def get_user_activity(
        self,
        request: UserActivityRequestDTO
    ) -> UserActivityResponseDTO:
        """Получение активности пользователя"""
        pass

    @abstractmethod
    async def search_users(
        self,
        request: UserSearchRequestDTO
    ) -> UserSearchResponseDTO:
        """Поиск пользователей"""
        pass
