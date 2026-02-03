""" Ответственность за блокировку учётных записей """


from datetime import datetime, timedelta, timezone
from sqlalchemy import and_
from typing import Optional

from backend.user_service.src.models import LoginAttempt


class AccountLocker:

    def __init__(self, config, db_session):
        self.config = config
        self.db = db_session

    def is_account_locked(self, email: str) -> tuple[bool, Optional[str]]:
        """
        Проверка блокировки аккаунта - возвращает (is_locked, error_message)
        """

        window_start = datetime.now(timezone.utc) - timedelta(
            minutes=self.config.LOGIN_ATTEMPT_WINDOW_MINUTES
        )
        count = self._get_failed_attempts_count_by_email(
            email,
            window_start
        )
        if count >= self.config.MAX_LOGIN_ATTEMPTS:
            lockout_end = datetime.now(timezone.utc) + timedelta(
                minutes=self.config.ACCOUNT_LOCKOUT_DURATION_MINUTES
            )
            return True, (
                f"Аккаунт заблокирован до "
                f"{lockout_end.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        return False, None

    def _get_failed_attempts_count_by_email(
            self,
            email: str,
            window_start: datetime
    ) -> int:
        """Подсчет неудачных попыток входа по email за период"""

        return self.db.query(LoginAttempt).filter(
            and_(
                LoginAttempt.email == email,
                LoginAttempt.is_successful is False,
                LoginAttempt.created_at >= window_start
            )
        ).count()
