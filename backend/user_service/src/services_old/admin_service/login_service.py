"""
Сервис для логирования и мониторинга входов
Обновлен для использования базового класса
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from sqlalchemy.exc import SQLAlchemyError

from backend.user_service.src.models import User
from common.base_service import BaseService


class LoginService(BaseService):
    """Сервис для логирования и мониторинга входов"""

    def __init__(self, db_session: Session):
        super().__init__()
        self.db_session = db_session

    def log_login_attempt(
        self,
        email: str,
        ip_address: str,
        user_agent: str = None,
        success: bool = False,
        failure_reason: str = None
    ) -> Dict[str, Any]:
        """Логирование попытки входа"""
        try:
            # Ищем пользователя
            user = self.db_session.query(User).filter(
                User.email == email).first()

            if user:
                # Обновляем данные пользователя
                user.last_login_ip = ip_address
                if hasattr(user, 'last_user_agent'):
                    user.last_user_agent = user_agent
                user.updated_at = datetime.now()

                if success:
                    user.last_login_at = datetime.now()

            self.db_session.commit()

            log_data = {
                "email": email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": success,
                "failure_reason": failure_reason,
                "timestamp": datetime.now().isoformat()
            }

            return self._handle_success(
                "Попытка входа залогирована",
                data=log_data
            )

        except SQLAlchemyError as e:
            self.db_session.rollback()
            return self._handle_error(e, "логирования попытки входа")

    def get_login_history(
        self,
        user_id: Optional[UUID] = None,
        email: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Получение истории входов"""
        try:
            if not user_id and not email:
                return self._handle_error(
                    "Необходимо указать user_id или email",
                    "получения истории входов"
                )

            # Определяем пользователя
            user = None
            if user_id:
                user = self.db_session.query(User).filter(
                    User.id == user_id).first()
            elif email:
                user = self.db_session.query(User).filter(
                    User.email == email).first()

            if not user:
                return self._handle_error(
                    "Пользователь не найден",
                    "получения истории входов"
                )

            # Получаем историю (упрощенная версия)
            # В реальном приложении должна быть отдельная таблица логов
            cutoff_date = datetime.now() - timedelta(days=days)

            # Пока что используем данные из таблицы пользователей
            history_data = {
                "user_id": str(user.id),
                "email": user.email,
                "period_days": days,
                "last_login": user.last_login_at.isoformat() if user.last_login_at else None,
                "last_login_ip": user.last_login_ip,
                "last_login_user_agent": getattr(user, 'last_user_agent', None),
                "account_created": user.created_at.isoformat(),
                "note": "Детальная история входов требует отдельной таблицы логов"
            }

            return self._handle_success(
                "История входов получена",
                data=history_data
            )

        except SQLAlchemyError as e:
            return self._handle_error(e, "получения истории входов")

    def get_failed_login_attempts(
        self,
        days: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Получение неудачных попыток входа"""
        try:
            # В реальном приложении здесь был бы запрос к таблице логов
            # Пока что возвращаем заглушку
            failed_attempts = []

            return self._handle_success(
                "Неудачные попытки входа получены",
                data={
                    "period_days": days,
                    "failed_attempts": failed_attempts,
                    "total_count": len(failed_attempts),
                    "note": "Требуется отдельная таблица логов для детальной информации"
                }
            )

        except SQLAlchemyError as e:
            return self._handle_error(e, "получения неудачных попыток входа")

    def get_suspicious_activity(
        self,
        days: int = 1,
        threshold: int = 5
    ) -> Dict[str, Any]:
        """Получение подозрительной активности"""
        try:
            # В реальном приложении здесь был бы анализ логов
            # Пока что возвращаем заглушку
            suspicious_activity = []

            return self._handle_success(
                "Подозрительная активность получена",
                data={
                    "period_days": days,
                    "threshold": threshold,
                    "suspicious_cases": suspicious_activity,
                    "total_count": len(suspicious_activity),
                    "note": "Требуется анализ логов для выявления подозрительной активности"
                }
            )

        except SQLAlchemyError as e:
            return self._handle_error(e, "получения подозрительной активности")

    def get_login_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Получение статистики входов"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            # Общее количество пользователей с входами за период
            users_with_logins = self.db_session.query(User).filter(
                and_(
                    User.last_login_at >= cutoff_date,
                    User.last_login_at.isnot(None)
                )
            ).count()

            # Пользователи, которые входили сегодня
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            users_today = self.db_session.query(User).filter(
                User.last_login_at >= today_start
            ).count()

            # Топ IP адресов по количеству входов
            # В реальном приложении это должен быть запрос к таблице логов
            top_ips = []

            return self._handle_success(
                "Статистика входов получена",
                data={
                    "period_days": days,
                    "users_with_logins": users_with_logins,
                    "users_today": users_today,
                    "top_ips": top_ips,
                    "generated_at": datetime.now().isoformat()
                }
            )

        except SQLAlchemyError as e:
            return self._handle_error(e, "получения статистики входов")
