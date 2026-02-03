"""
Специализированный класс для работы с попытками входа
(анализ логов, сбор статистики)
"""


from typing import Optional
from datetime import datetime, timezone, timedelta
from uuid import UUID


from user_service.models import LoginAttempt
from user_service.repository import UserRepository


class LoginAttemptsService:
    """Сервис для работы с попытками входа"""

    def __init__(self, db_session):
        self.repository = UserRepository(db_session)

    def get_login_logs(
        self,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        days: int = 7,
        limit: int = 100
    ):
        """Получение логов входов"""

        since_date = datetime.now(timezone.utc) - timedelta(days=days)

        query = self.repository.get_query().filter(
            LoginAttempt.created_at >= since_date
        )

        if user_id:
            query = query.filter(LoginAttempt.user_id == str(user_id))

        if ip_address:
            query = query.filter(LoginAttempt.ip_address == ip_address)

        return query.order_by(
            LoginAttempt.created_at.desc()).limit(limit).all()
