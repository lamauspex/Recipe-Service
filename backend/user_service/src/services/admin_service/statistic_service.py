"""
Отдельный класс для сбора статистики и формирования отчётов
(общая активность, успешные и неуспешные попытки входа, новые регистрации)
"""

from typing import List
from datetime import datetime, timezone, timedelta

from backend.user_service.src.models import LoginAttempt, User
from backend.user_service.src.schemas.user_roles import UserRole
from backend.user_service.src.repository import UserRepository


class StatisticsService:
    """Класс для сбора статистики """

    def __init__(self, db_session):
        self.repository = UserRepository(db_session)

    def get_admin_stats(self) -> dict:
        """Получение общей статистики"""

        total_users = self.repository.db.query(User).count()

        active_users = self.repository.db.query(
            User).filter(User.is_active is True).count()

        admin_users = self.repository.db.query(User).filter(
            User.role == UserRole.ADMIN).count()

        return {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users
        }

    def get_recent_registrations(
        self,
        days: int = 7
    ) -> List[User]:
        """Получение недавно зарегистрированных пользователей"""

        since_date = datetime.now(timezone.utc) - timedelta(days=days)

        return self.repository.db.query(User).filter(
            User.created_at >= since_date).order_by(
                User.created_at.desc()).all()

    def get_login_attempts_stats(
        self,
        days: int = 7
    ) -> dict:
        """Статистика попыток входа"""

        since_date = datetime.now(timezone.utc) - timedelta(days=days)

        total_attempts = self.repository.db.query(LoginAttempt).filter(
            LoginAttempt.created_at >= since_date).count()

        successful_attempts = self.repository.db.query(LoginAttempt).filter(
            LoginAttempt.created_at >= since_date,
            LoginAttempt.is_successful is True).count()

        failed_attempts = total_attempts - successful_attempts

        return {
            "total_attempts": total_attempts,
            "successful_attempts": successful_attempts,
            "failed_attempts": failed_attempts,
            "success_rate": (
                successful_attempts / total_attempts * 100
            ) if total_attempts > 0 else 0
        }
