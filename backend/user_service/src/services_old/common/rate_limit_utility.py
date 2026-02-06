"""
Утилита для работы с лимитами запросов
Устраняет дублирование логики для email и IP адресов
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from backend.user_service.src.models import User
from common.response_builder import ResponseBuilder


class RateLimitUtility:
    """Утилита для работы с лимитами запросов"""

    def __init__(self, db_session: Session, max_per_hour: int = 5, max_per_day: int = 20):
        self.db_session = db_session
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day

    def _get_attempts_count(self, identifier: str, identifier_field: str, time_window: timedelta) -> int:
        """Получение количества попыток за временное окно"""
        cutoff_time = datetime.now() - time_window

        return self.db_session.query(User).filter(
            and_(
                getattr(User, identifier_field) == identifier,
                User.updated_at >= cutoff_time
            )
        ).count()

    def check_rate_limit(self, email: str = None, ip_address: str = None) -> Tuple[bool, Optional[str]]:
        """Проверка лимита запросов для email или IP"""
        current_time = datetime.now()

        # Проверяем по email
        if email:
            if not self._check_identifier_limits(email, 'email'):
                return False, f"Превышен лимит запросов для {email}"

        # Проверяем по IP
        if ip_address:
            if not self._check_identifier_limits(ip_address, 'last_login_ip'):
                return False, f"Превышен лимит запросов с IP {ip_address}"

        return True, None

    def _check_identifier_limits(self, identifier: str, identifier_field: str) -> bool:
        """Проверка лимитов для конкретного идентификатора"""
        attempts_hour = self._get_attempts_count(
            identifier, identifier_field, timedelta(hours=1))
        attempts_day = self._get_attempts_count(
            identifier, identifier_field, timedelta(days=1))

        return attempts_hour < self.max_per_hour and attempts_day < self.max_per_day

    def get_limit_info(self, email: str = None, ip_address: str = None) -> Dict[str, Any]:
        """Получение информации о лимитах"""
        try:
            if not email and not ip_address:
                return ResponseBuilder.error(
                    "Необходимо указать email или IP адрес",
                    error_code="MISSING_PARAMETERS"
                )

            if email:
                return self._get_email_limit_info(email)
            elif ip_address:
                return self._get_ip_limit_info(ip_address)

        except SQLAlchemyError as e:
            return ResponseBuilder.error(
                f"Ошибка получения информации о лимитах: {str(e)}",
                error_code="DATABASE_ERROR"
            )

    def _get_email_limit_info(self, email: str) -> Dict[str, Any]:
        """Получение информации о лимитах для email"""
        attempts_hour = self._get_attempts_count(
            email, 'email', timedelta(hours=1))
        attempts_day = self._get_attempts_count(
            email, 'email', timedelta(days=1))

        return {
            "email": email,
            "attempts_this_hour": attempts_hour,
            "attempts_this_day": attempts_day,
            "max_per_hour": self.max_per_hour,
            "max_per_day": self.max_per_day,
            "hourly_remaining": max(0, self.max_per_hour - attempts_hour),
            "daily_remaining": max(0, self.max_per_day - attempts_day),
            "success": True,
            "timestamp": datetime.now().isoformat()
        }

    def _get_ip_limit_info(self, ip_address: str) -> Dict[str, Any]:
        """Получение информации о лимитах для IP адреса"""
        attempts_hour = self._get_attempts_count(
            ip_address, 'last_login_ip', timedelta(hours=1))
        attempts_day = self._get_attempts_count(
            ip_address, 'last_login_ip', timedelta(days=1))

        return {
            "ip_address": ip_address,
            "attempts_this_hour": attempts_hour,
            "attempts_this_day": attempts_day,
            "max_per_hour": self.max_per_hour,
            "max_per_day": self.max_per_day,
            "hourly_remaining": max(0, self.max_per_hour - attempts_hour),
            "daily_remaining": max(0, self.max_per_day - attempts_day),
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
