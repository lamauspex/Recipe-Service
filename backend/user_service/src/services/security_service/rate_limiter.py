"""Класс RateLimiter для ограничения частоты запросов"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from backend.user_service.src.models import User


logger = logging.getLogger(__name__)


class RateLimiter:
    """Класс для ограничения частоты запросов"""

    def __init__(self, config, db_session: Session):
        self.config = config
        self.db_session = db_session
        self.max_attempts_per_hour = getattr(
            config, 'MAX_LOGIN_ATTEMPTS_PER_HOUR', 5)
        self.max_attempts_per_day = getattr(
            config, 'MAX_LOGIN_ATTEMPTS_PER_DAY', 20)

    def check_rate_limit(
        self,
        ip_address: str,
        email: str = None
    ) -> Tuple[bool, Optional[str]]:
        """Проверка лимита запросов"""

        try:
            current_time = datetime.now()
            one_hour_ago = current_time - timedelta(hours=1)
            one_day_ago = current_time - timedelta(days=1)

            # Проверяем по IP адресу
            if ip_address:
                ip_attempts_hour = self.db_session.query(User).filter(
                    and_(
                        User.last_login_ip == ip_address,
                        User.updated_at >= one_hour_ago
                    )
                ).count()

                if ip_attempts_hour >= self.max_attempts_per_hour:
                    return False, f"Превышен лимит запросов с IP {ip_address} (час)"

                ip_attempts_day = self.db_session.query(User).filter(
                    and_(
                        User.last_login_ip == ip_address,
                        User.updated_at >= one_day_ago
                    )
                ).count()

                if ip_attempts_day >= self.max_attempts_per_day:
                    return False, f"Превышен лимит запросов с IP {ip_address} (день)"

            # Проверяем по email
            if email:
                email_attempts_hour = self.db_session.query(User).filter(
                    and_(
                        User.email == email,
                        User.updated_at >= one_hour_ago
                    )
                ).count()

                if email_attempts_hour >= self.max_attempts_per_hour:
                    return False, f"Превышен лимит запросов для {email} (час)"

                email_attempts_day = self.db_session.query(User).filter(
                    and_(
                        User.email == email,
                        User.updated_at >= one_day_ago
                    )
                ).count()

                if email_attempts_day >= self.max_attempts_per_day:
                    return False, f"Превышен лимит запросов для {email} (день)"

            return True, None

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при проверке лимита для {email}: {e}")
            return False, "Ошибка проверки лимита"

    def get_limit_info(
        self,
        email: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> dict:
        """Получение информации о лимитах - единый метод"""

        try:
            # Валидация в сервисе (не в роутере!)
            if not email and not ip_address:
                return {
                    "error": "Необходимо указать email или IP адрес",
                    "success": False
                }

            # Логика выбора в сервисе (не в роутере!)
            if email:
                return self.get_email_limit_info(email)
            elif ip_address:
                return self.get_ip_limit_info(ip_address)

        except Exception as e:
            logger.error(f"Ошибка при получении лимитов: {e}")
            return {
                "error": f"Ошибка получения информации о лимитах: {str(e)}",
                "success": False
            }

    def get_email_limit_info(self, email: str) -> dict:
        """Получение информации о лимитах для email"""

        try:
            current_time = datetime.now()
            one_hour_ago = current_time - timedelta(hours=1)
            one_day_ago = current_time - timedelta(days=1)

            attempts_hour = self.db_session.query(User).filter(
                and_(
                    User.email == email,
                    User.updated_at >= one_hour_ago
                )
            ).count()

            attempts_day = self.db_session.query(User).filter(
                and_(
                    User.email == email,
                    User.updated_at >= one_day_ago
                )
            ).count()

            return {
                "email": email,
                "attempts_this_hour": attempts_hour,
                "attempts_this_day": attempts_day,
                "max_per_hour": self.max_attempts_per_hour,
                "max_per_day": self.max_attempts_per_day,
                "hourly_remaining": max(0, self.max_attempts_per_hour - attempts_hour),
                "daily_remaining": max(0, self.max_attempts_per_day - attempts_day),
                "success": True
            }

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении лимитов для {email}: {e}")
            return {
                "error": f"Ошибка получения информации о лимитах: {str(e)}",
                "success": False
            }

    def get_ip_limit_info(self, ip_address: str) -> dict:
        """Получение информации о лимитах для IP адреса"""

        try:
            current_time = datetime.now()
            one_hour_ago = current_time - timedelta(hours=1)
            one_day_ago = current_time - timedelta(days=1)

            attempts_hour = self.db_session.query(User).filter(
                and_(
                    User.last_login_ip == ip_address,
                    User.updated_at >= one_hour_ago
                )
            ).count()

            attempts_day = self.db_session.query(User).filter(
                and_(
                    User.last_login_ip == ip_address,
                    User.updated_at >= one_day_ago
                )
            ).count()

            return {
                "ip_address": ip_address,
                "attempts_this_hour": attempts_hour,
                "attempts_this_day": attempts_day,
                "max_per_hour": self.max_attempts_per_hour,
                "max_per_day": self.max_attempts_per_day,
                "hourly_remaining": max(0, self.max_attempts_per_hour - attempts_hour),
                "daily_remaining": max(0, self.max_attempts_per_day - attempts_day),
                "success": True
            }

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении лимитов для {ip_address}: {e}")
            return {
                "error": f"Ошибка получения информации о лимитах: {str(e)}",
                "success": False
            }
