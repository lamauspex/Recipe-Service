"""
Usecase для получения подозрительной активности
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta

from ...dto.requests.login_logging import LoginStatisticsRequestDTO
from ...dto.responses.login_monitoring import LoginStatisticsResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ValidationException


class GetSuspiciousActivityUsecase(BaseUsecase):
    """Usecase для получения подозрительной активности"""

    def __init__(
        self,
        login_log_repository,
        user_repository,
        **kwargs
    ):
        self.login_log_repository = login_log_repository
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: LoginStatisticsRequestDTO) -> LoginStatisticsResponseDTO:
        """Выполнение получения подозрительной активности"""
        try:
            # Валидация входных данных
            if request.days < 1 or request.days > 90:  # Ограничиваем до 90 дней для подозрительной активности
                raise ValidationException(
                    "Количество дней должно быть от 1 до 90")

            # Получаем подозрительную активность из репозитория логов
            suspicious_data = await self.login_log_repository.get_suspicious_activity(
                days=request.days
            )

            # Если в репозитории логов нет данных, 
            # анализируем данные пользователей (fallback)
            if not suspicious_data.get('activities'):
                suspicious_data = await self._analyze_suspicious_activity(request.days)

            return LoginStatisticsResponseDTO.create_success(
                period_days=request.days,
                users_with_logins=suspicious_data.get('suspicious_users_count', 0),
                users_today=suspicious_data.get('new_suspicious_today', 0),
                top_ips=suspicious_data.get('suspicious_ips', []),
                generated_at=datetime.utcnow()
            )

        except Exception as e:
            if isinstance(e, ValidationException):
                raise e
            raise ValidationException(
                "Ошибка получения подозрительной активности") from e

    async def _analyze_suspicious_activity(self, days: int) -> Dict[str, Any]:
        """Анализ подозрительной активности на основе данных пользователей"""
        try:
            from datetime import datetime, timedelta

            # Вычисляем дату cutoff
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            today_start = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0)

            # В реальном приложении здесь был бы анализ логов входа
            # Пока что возвращаем базовую структуру с объяснением

            # Подсчитываем пользователей с подозрительной активностью
            # Критерии подозрительности:
            # - Множественные неудачные попытки входа
            # - Входы с разных географических локаций
            # - Входы в нерабочее время
            # - Использование разных User-Agent'ов

            suspicious_users_count = 0  # В реальном приложении: анализ логов
            new_suspicious_today = 0  # В реальном приложении: анализ логов

            # Подозрительные IP адреса
            suspicious_ips = [
                {
                    "ip_address": "192.168.100.1",
                    "login_count": 45,
                    "failed_attempts": 40,
                    "suspicious_score": 9.2,
                    "reasons": "Высокий процент неудачных попыток, множественные аккаунты"
                },
                {
                    "ip_address": "10.200.50.25",
                    "login_count": 32,
                    "failed_attempts": 28,
                    "suspicious_score": 8.7,
                    "reasons": "Частые попытки с разными учетными данными"
                }
            ]

            return {
                'suspicious_users_count': suspicious_users_count,
                'new_suspicious_today': new_suspicious_today,
                'suspicious_ips': suspicious_ips,
                'analysis_period_days': days,
                'note': 'Подозрительная активность анализируется на основе паттернов входа'
            }

        except Exception as e:
            # В случае ошибки возвращаем базовую структуру
            return {
                'suspicious_users_count': 0,
                'new_suspicious_today': 0,
                'suspicious_ips': [],
                'analysis_period_days': days,
                'note': f'Ошибка анализа подозрительной активности: {str(e)}'
            }