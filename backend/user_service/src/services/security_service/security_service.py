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

    def block_ip_address(
        self,
        ip_address: str,
        reason: str,
        duration_hours: Optional[int] = None,
        admin_id: Optional[str] = None
    ) -> dict:
        """Блокировка IP адреса - возвращает готовый ответ"""

        try:
            self.ip_blocker.block_ip_address(
                ip_address,
                duration_hours,
                reason
            )
            return {
                "message": f"IP адрес {ip_address} заблокирован",
                "success": True
            }
        except Exception as e:
            return {
                "error": f"Не удалось заблокировать {ip_address}: {str(e)}",
                "success": False
            }
