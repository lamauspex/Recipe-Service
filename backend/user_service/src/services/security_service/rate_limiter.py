
""" Логика ограничения частоты запросов (rate limiting) """


from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy import and_, select

from backend.user_service.src.models import LoginAttempt


class RateLimiter:
    """ Логика ограничения частоты запросов """

    def __init__(self, config, db_session):
        self.config = config
        self.db = db_session

    def check_rate_limit(
        self,
        ip_address: str,
        email: str = None
    ) -> tuple[bool, Optional[str]]:
        """Проверка rate limiting - возвращает (success, error_message)"""

        window_start = datetime.now(timezone.utc) - timedelta(
            minutes=self.config.LOGIN_ATTEMPT_WINDOW_MINUTES
        )
        attempts = self._get_unsuccessful_attempts_by_ip(
            ip_address,
            window_start
        )
        if len(attempts) >= self.config.MAX_LOGIN_ATTEMPTS:
            return False, "Слишком много неудачных попыток"

        return True, None

    def _get_unsuccessful_attempts_by_ip(
        self,
        ip_address: str,
        window_start: datetime
    ) -> List[LoginAttempt]:
        """Получение неудачных попыток входа по IP за период"""

        return self.db.execute(select(LoginAttempt).where(
            and_(
                LoginAttempt.ip_address == ip_address,
                LoginAttempt.is_successful is False,
                LoginAttempt.created_at >= window_start
            ))
        ).scalars().all()
