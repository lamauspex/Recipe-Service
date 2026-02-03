"""
Обнаружение подозрительной активности
(множественные IP, странные User Agents)
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import and_
from typing import Set

from backend.user_service.src.models import LoginAttempt


class SuspiciousDetector:
    """ Сервис для работы """

    def __init__(self, config, db_session):
        self.config = config
        self.db = db_session

    def detect_suspicious_activity(
        self,
        email: str,
        user_agent: str,
        ip_address: str = None
    ) -> bool:
        """ Обнаружение подозрительной активности """

        # Проверка на множественные IP для одного email
        recent_time = datetime.now(timezone.utc) - timedelta(
            hours=self.config.SUSPICIOUS_ACTIVITY_HOURS_WINDOW
        )
        if self._has_multiple_ips_for_email(
            email,
            recent_time
        ):
            return True

        # Проверка на подозрительные User-Agent
        if self._has_suspicious_user_agent(user_agent):
            return True

        return False

    def _has_multiple_ips_for_email(
        self,
        email: str,
        window_start: datetime
    ) -> bool:
        """Проверка множественных IP для одного email"""

        recent_attempts = self.db.query(LoginAttempt).filter(
            and_(
                LoginAttempt.email == email,
                LoginAttempt.created_at >= window_start
            )
        ).all()

        unique_ips: Set[str] = {
            attempt.ip_address for attempt in recent_attempts
        }

        # Если более N разных IP за период - подозрительно
        return len(unique_ips) > self.config.MAX_UNIQUE_IPS_PER_EMAIL

    def _has_suspicious_user_agent(self, user_agent: str) -> bool:
        """ Проверка подозрительных User-Agent """

        user_agent_lower = user_agent.lower()

        return any(
            suspicious_agent in user_agent_lower
            for suspicious_agent in self.config.SUSPICIOUS_USER_AGENTS
        )
