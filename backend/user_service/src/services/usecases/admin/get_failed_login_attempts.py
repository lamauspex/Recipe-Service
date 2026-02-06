"""
Usecase для получения неудачных попыток входа
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta

from ...dto.requests.login_logging import LoginStatisticsRequestDTO
from ...dto.responses.login_monitoring import FailedLoginAttemptsResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ValidationException


class GetFailedLoginAttemptsUsecase(BaseUsecase):
    """Usecase для получения неудачных попыток входа"""

    def __init__(
        self,
        login_log_repository,
        user_repository,
        **kwargs
    ):
        self.login_log_repository = login_log_repository
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: LoginStatisticsRequestDTO) -> FailedLoginAttemptsResponseDTO:
        """Выполнение получения неудачных попыток входа"""
        try:
            # Валидация входных данных
            if request.days < 1 or request.days > 365:
                raise ValidationException(
                    "Количество дней должно быть от 1 до 365")

            # Получаем неудачные попытки из репозитория логов
            failed_attempts_data = await self.login_log_repository.get_failed_login_attempts(
                days=request.days
            )

            # Если в репозитории логов нет данных, 
            # получаем их из пользователей (fallback)
            if not failed_attempts_data:
                failed_attempts_data = await self._get_failed_attempts_from_users(request.days)

            # Преобразуем данные в формат ответа
            formatted_attempts = []
            for attempt in failed_attempts_data:
                formatted_attempt = {
                    "timestamp": attempt.get('timestamp', datetime.utcnow()).isoformat(),
                    "email": attempt.get('email', ''),
                    "ip_address": attempt.get('ip_address', ''),
                    "user_agent": attempt.get('user_agent'),
                    "failure_reason": attempt.get('failure_reason', 'Неизвестная ошибка')
                }
                formatted_attempts.append(formatted_attempt)

            return FailedLoginAttemptsResponseDTO.create_success(
                period_days=request.days,
                failed_attempts=formatted_attempts,
                note=f"Найдено {len(formatted_attempts)} неудачных попыток входа за последние {request.days} дней"
            )

        except Exception as e:
            if isinstance(e, ValidationException):
                raise e
            raise ValidationException(
                "Ошибка получения неудачных попыток входа") from e

    async def _get_failed_attempts_from_users(self, days: int) -> List[Dict[str, Any]]:
        """Получение неудачных попыток на основе данных пользователей (fallback)"""
        try:
            # Вычисляем дату cutoff
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # В реальном приложении здесь был бы запрос к логам входа
            # Пока что возвращаем пустой список с объяснением
            return []

        except Exception as e:
            # В случае ошибки возвращаем пустой список
            return []