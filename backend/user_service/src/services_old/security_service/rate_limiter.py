import logging
from typing import Optional, Dict, Any

from common.base_service import BaseService
from common.rate_limit_utility import RateLimitUtility


logger = logging.getLogger(__name__)


class RateLimiter(BaseService):
    """Класс для ограничения частоты запросов"""

    def __init__(self, config, db_session):
        super().__init__()
        self.config = config
        self.max_attempts_per_hour = getattr(
            config, 'MAX_LOGIN_ATTEMPTS_PER_HOUR', 5)
        self.max_attempts_per_day = getattr(
            config, 'MAX_LOGIN_ATTEMPTS_PER_DAY', 20)

        # Используем утилиту для работы с лимитами
        self.rate_limit_utility = RateLimitUtility(
            db_session=db_session,
            max_per_hour=self.max_attempts_per_hour,
            max_per_day=self.max_attempts_per_day
        )

    def check_rate_limit(
        self,
        ip_address: str,
        email: str = None
    ) -> Dict[str, Any]:
        """Проверка лимита запросов"""
        try:
            is_allowed, message = self.rate_limit_utility.check_rate_limit(
                email=email,
                ip_address=ip_address
            )

            if is_allowed:
                return self._handle_success("Лимит не превышен")
            else:
                return self._handle_error(Exception(message), "проверки лимита")

        except Exception as e:
            return self._handle_error(e, "проверки лимита")

    def get_limit_info(
        self,
        email: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получение информации о лимитах"""
        try:
            return self.rate_limit_utility.get_limit_info(email=email, ip_address=ip_address)

        except Exception as e:
            return self._handle_error(e, "получения информации о лимитах")
