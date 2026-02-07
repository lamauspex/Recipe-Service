""" Основной сервис, объединяющий все компоненты """


from typing import Optional
from .account_locker import AccountLocker
from .ip_blocker import IpBlocker
from .rate_limiter import RateLimiter
from .suspicious_detector import SuspiciousDetector


class SecurityService:
    """Базовый сервис безопасности"""

    def __init__(self, db_session, config):
        self.db_session = db_session
        self.config = config
        self.ip_blocker = IpBlocker(config)
        self.rate_limiter = RateLimiter(config, db_session)
        self.account_locker = AccountLocker(config, db_session)
        self.suspicious_detector = SuspiciousDetector(config, db_session)

    def check_security(
        self,
        email: str,
        ip_address: str,
        user_agent: str
    ) -> tuple[bool, Optional[str]]:
        """Проверка безопасности"""

        result, message = self.rate_limiter.check_rate_limit(
            ip_address,
            email
        )

        if not result:
            return False, message

        locked, lock_message = self.account_locker.is_account_locked(email)

        if locked:
            return False, lock_message

        if self.suspicious_detector.detect_suspicious_activity(
            email,
            user_agent
        ):
            return False, "Обнаружено подозрительное поведение"

        return True, None
