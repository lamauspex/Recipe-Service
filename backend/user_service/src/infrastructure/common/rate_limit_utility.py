"""
Утилита для работы с лимитами запросов
Перенесено из старой архитектуры с улучшениями
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple


class RateLimitUtility:
    """Утилита для работы с лимитами запросов"""

    def __init__(self, user_repository=None, max_per_hour: int = 5, max_per_day: int = 20):
        self.user_repository = user_repository
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day

    async def check_rate_limit(self, email: str = None, ip_address: str = None) -> Tuple[bool, Optional[str]]:
        """Проверка лимита запросов для email или IP"""
        try:
            # Проверяем по email
            if email:
                if not await self._check_identifier_limits(email, 'email'):
                    return False, f"Rate limit exceeded for {email}"

            # Проверяем по IP
            if ip_address:
                if not await self._check_identifier_limits(ip_address, 'last_login_ip'):
                    return False, f"Rate limit exceeded for IP {ip_address}"

            return True, None

        except Exception as e:
            return False, f"Rate limit check failed: {str(e)}"

    async def _check_identifier_limits(self, identifier: str, identifier_field: str) -> bool:
        """Проверка лимитов для конкретного идентификатора"""
        try:
            # Проверяем лимит за последний час
            attempts_hour = await self._get_attempts_count(
                identifier, identifier_field, timedelta(hours=1))

            # Проверяем лимит за последний день
            attempts_day = await self._get_attempts_count(
                identifier, identifier_field, timedelta(days=1))

            return attempts_hour < self.max_per_hour and attempts_day < self.max_per_day

        except Exception:
            return False

    async def _get_attempts_count(self, identifier: str, identifier_field: str, time_window: timedelta) -> int:
        """Получение количества попыток за временное окно"""
        try:
            cutoff_time = datetime.utcnow() - time_window

            # Это заглушка - в реальной реализации здесь был бы запрос к БД
            # Временная заглушка возвращает 0
            return 0

        except Exception:
            return 0

    async def get_limit_info(self, email: str = None, ip_address: str = None) -> Dict[str, Any]:
        """Получение информации о лимитах"""
        try:
            if not email and not ip_address:
                return {
                    "error": "Either email or IP address must be provided",
                    "success": False
                }

            if email:
                return await self._get_email_limit_info(email)
            elif ip_address:
                return await self._get_ip_limit_info(ip_address)

        except Exception as e:
            return {
                "error": f"Failed to get limit info: {str(e)}",
                "success": False
            }

    async def _get_email_limit_info(self, email: str) -> Dict[str, Any]:
        """Получение информации о лимитах для email"""
        try:
            attempts_hour = await self._get_attempts_count(
                email, 'email', timedelta(hours=1))
            attempts_day = await self._get_attempts_count(
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
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "error": f"Failed to get email limit info: {str(e)}",
                "success": False
            }

    async def _get_ip_limit_info(self, ip_address: str) -> Dict[str, Any]:
        """Получение информации о лимитах для IP адреса"""
        try:
            attempts_hour = await self._get_attempts_count(
                ip_address, 'last_login_ip', timedelta(hours=1))
            attempts_day = await self._get_attempts_count(
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
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "error": f"Failed to get IP limit info: {str(e)}",
                "success": False
            }
