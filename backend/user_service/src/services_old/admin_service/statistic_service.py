"""
Сервис статистики
Обновлен для использования базового класса
"""

from datetime import datetime, timedelta
from typing import Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from backend.user_service.src.models import User
from common.base_service import BaseService


class StatisticService(BaseService):
    """Класс для работы со статистикой"""

    def __init__(self, db_session: Session):
        super().__init__()
        self.db_session = db_session

    def get_user_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Получение статистики пользователей"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Общее количество пользователей
            total_users = self.db_session.query(User).count()

            # Новые пользователи за период
            new_users = self.db_session.query(User).filter(
                and_(
                    User.created_at >= start_date,
                    User.created_at <= end_date
                )
            ).count()

            # Активные пользователи
            active_users = self.db_session.query(User).filter(
                User.is_active == True
            ).count()

            # Заблокированные пользователи
            locked_users = self.db_session.query(User).filter(
                User.is_locked == True
            ).count()

            # Статистика по дням
            daily_stats = self._get_daily_registration_stats(
                start_date, end_date)

            return self._handle_success(
                "Статистика пользователей получена",
                data={
                    "period_days": days,
                    "total_users": total_users,
                    "new_users": new_users,
                    "active_users": active_users,
                    "locked_users": locked_users,
                    "daily_registrations": daily_stats,
                    "generated_at": datetime.now().isoformat()
                }
            )

        except SQLAlchemyError as e:
            return self._handle_error(e, "получения статистики пользователей")

    def get_login_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Получение статистики входов"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Общее количество входов
            total_logins = self.db_session.query(User).filter(
                and_(
                    User.last_login_at >= start_date,
                    User.last_login_at <= end_date
                )
            ).count()

            # Уникальные пользователи, которые входили
            unique_logins = self.db_session.query(User).filter(
                and_(
                    User.last_login_at >= start_date,
                    User.last_login_at <= end_date,
                    User.last_login_at.isnot(None)
                )
            ).count()

            # Статистика по дням
            daily_logins = self._get_daily_login_stats(start_date, end_date)

            return self._handle_success(
                "Статистика входов получена",
                data={
                    "period_days": days,
                    "total_logins": total_logins,
                    "unique_users_logged_in": unique_logins,
                    "daily_logins": daily_logins,
                    "generated_at": datetime.now().isoformat()
                }
            )

        except SQLAlchemyError as e:
            return self._handle_error(e, "получения статистики входов")

    def get_security_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Получение статистики безопасности"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Заблокированные аккаунты
            locked_accounts = self.db_session.query(User).filter(
                User.is_locked == True
            ).count()

            # Недавно заблокированные
            recently_locked = self.db_session.query(User).filter(
                and_(
                    User.is_locked == True,
                    User.updated_at >= start_date
                )
            ).count()

            # Аккаунты с неподтвержденным email
            unverified_emails = self.db_session.query(User).filter(
                User.email_verified == False
            ).count()

            return self._handle_success(
                "Статистика безопасности получена",
                data={
                    "period_days": days,
                    "locked_accounts": locked_accounts,
                    "recently_locked": recently_locked,
                    "unverified_emails": unverified_emails,
                    "generated_at": datetime.now().isoformat()
                }
            )

        except SQLAlchemyError as e:
            return self._handle_error(e, "получения статистики безопасности")

    def get_overall_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Получение общей статистики"""
        try:
            # Получаем все виды статистики
            user_stats = self.get_user_statistics(days)
            login_stats = self.get_login_statistics(days)
            security_stats = self.get_security_statistics(days)

            # Объединяем данные
            overall_data = {
                "period_days": days,
                "generated_at": datetime.now().isoformat(),
                "user_statistics": user_stats.get("data", {}),
                "login_statistics": login_stats.get("data", {}),
                "security_statistics": security_stats.get("data", {}),
            }

            return self._handle_success(
                "Общая статистика получена",
                data=overall_data
            )

        except Exception as e:
            return self._handle_error(e, "получения общей статистики")

    def _get_daily_registration_stats(self, start_date: datetime, end_date: datetime) -> list:
        """Получение статистики регистраций по дням"""
        daily_stats = []
        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            next_date = current_date + timedelta(days=1)

            count = self.db_session.query(User).filter(
                and_(
                    User.created_at >= current_date,
                    User.created_at < next_date
                )
            ).count()

            daily_stats.append({
                "date": current_date.isoformat(),
                "registrations": count
            })

            current_date = next_date

        return daily_stats

    def _get_daily_login_stats(self, start_date: datetime, end_date: datetime) -> list:
        """Получение статистики входов по дням"""
        daily_stats = []
        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            next_date = current_date + timedelta(days=1)

            count = self.db_session.query(User).filter(
                and_(
                    User.last_login_at >= current_date,
                    User.last_login_at < next_date,
                    User.last_login_at.isnot(None)
                )
            ).count()

            daily_stats.append({
                "date": current_date.isoformat(),
                "logins": count
            })

            current_date = next_date

        return daily_stats
