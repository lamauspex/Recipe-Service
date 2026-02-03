"""
Rate limiting

Реализация rate limiting на основе IP адреса
"""

from __future__ import annotations


import logging
from collections import defaultdict
from typing import Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from backend.user_service.src.config import settings


@dataclass
class RateLimitInfo:
    """Информация о rate limit для IP"""
    requests: list = field(default_factory=list)
    blocked_until: Optional[datetime] = None

    def add_request(self, timestamp: datetime) -> None:
        """Добавление нового запроса"""
        self.requests.append(timestamp)

    def get_recent_requests(
        self,
        window: timedelta
    ) -> list:
        """Получение запросов в указанном окне"""
        cutoff = datetime.utcnow() - window
        return [t for t in self.requests if t > cutoff]

    def is_blocked(self) -> bool:
        """Проверка, заблокирован ли IP"""
        if self.blocked_until:
            if datetime.utcnow() < self.blocked_until:
                return True
            # Разблокируем, если время истекло
            self.blocked_until = None
        return False


class RateLimiter:
    """
    Rate limiter на основе IP адреса

    Соответствует принципу единственной ответственности (SRP):
    - Только логика rate limiting
    - Никакой бизнес-логики
    """

    def __init__(
        self,
        requests_per_minute: int = None,
        requests_per_hour: int = None,
        block_duration_seconds: int = None,
        window_size_seconds: int = 60
    ):
        self.logger = logging.getLogger("rate_limiting")

        # Настройки rate limiting
        self.requests_per_minute = requests_per_minute or settings.auth.RATE_LIMIT_REQUESTS_PER_MINUTE
        self.requests_per_hour = requests_per_hour or settings.auth.RATE_LIMIT_REQUESTS_PER_HOUR
        self.block_duration_seconds = block_duration_seconds or settings.auth.RATE_LIMIT_BLOCK_DURATION
        self.window_size_seconds = window_size_seconds

        # Хранилище для отслеживания запросов
        self._ip_requests: Dict[
            str,
            RateLimitInfo
        ] = defaultdict(RateLimitInfo)

        # Время последней очистки
        self._last_cleanup = datetime.utcnow()

    def is_allowed(self, ip_address: str) -> Tuple[bool, int]:
        """
        Проверка, разрешен ли запрос для IP

        Args:
            ip_address: IP адрес клиента

        Returns:
            Tuple[bool, int]: 
            (разрешен ли запрос, количество оставшихся запросов)
        """
        rate_info = self._ip_requests[ip_address]

        # Проверяем, заблокирован ли IP
        if rate_info.is_blocked():
            blocked_seconds = int(
                (rate_info.blocked_until - datetime.utcnow()).total_seconds()
            )
            self.logger.warning(
                f"IP {ip_address} заблокирован. "
                f"Осталось {blocked_seconds} секунд"
            )
            return False, 0

        # Проверяем rate limit
        now = datetime.utcnow()
        minute_window = timedelta(seconds=60)
        hour_window = timedelta(seconds=3600)

        # Проверяем минутный лимит
        recent_minute = rate_info.get_recent_requests(minute_window)
        if len(recent_minute) >= self.requests_per_minute:
            self._block_ip(rate_info, ip_address)
            return False, 0

        # Проверяем часовой лимит
        recent_hour = rate_info.get_recent_requests(hour_window)
        if len(recent_hour) >= self.requests_per_hour:
            self._block_ip(rate_info, ip_address)
            return False, 0

        # Добавляем запрос
        rate_info.add_request(now)

        # Вычисляем оставшиеся запросы
        remaining = min(
            self.requests_per_minute - len(recent_minute) - 1,
            self.requests_per_hour - len(recent_hour) - 1
        )

        self.logger.debug(f"IP {ip_address} - осталось запросов: {remaining}")
        return True, max(0, remaining)

    def get_rate_limit_info(self, ip_address: str) -> Dict:
        """
        Получение информации о rate limit для IP

        Args:
            ip_address: IP адрес клиента

        Returns:
            Dict: Информация о rate limit
        """
        rate_info = self._ip_requests.get(ip_address, RateLimitInfo())
        now = datetime.utcnow()

        minute_window = timedelta(seconds=60)
        hour_window = timedelta(seconds=3600)

        recent_minute = rate_info.get_recent_requests(minute_window)
        recent_hour = rate_info.get_recent_requests(hour_window)

        info = {
            "requests_last_minute": len(recent_minute),
            "requests_last_hour": len(recent_hour),
            "limit_per_minute": self.requests_per_minute,
            "limit_per_hour": self.requests_per_hour,
            "remaining_per_minute": max(
                0,
                self.requests_per_minute - len(recent_minute)
            ),
            "remaining_per_hour": max(
                0,
                self.requests_per_hour - len(recent_hour)
            ),
            "is_blocked": rate_info.is_blocked()
        }

        if rate_info.blocked_until:
            info["blocked_until"] = rate_info.blocked_until.isoformat()
            info["blocked_seconds_remaining"] = int(
                (rate_info.blocked_until - now).total_seconds()
            )

        return info

    def _block_ip(self, rate_info: RateLimitInfo, ip_address: str) -> None:
        """Блокировка IP адреса"""
        rate_info.blocked_until = datetime.utcnow() + timedelta(
            seconds=self.block_duration_seconds
        )

        self.logger.warning(
            f"IP {ip_address} заблокирован на "
            f"{self.block_duration_seconds} секунд "
            f"из-за превышения rate limit"
        )

    def unblock_ip(self, ip_address: str) -> bool:
        """
        Разблокировка IP адреса

        Args:
            ip_address: IP адрес клиента

        Returns:
            bool: Был ли IP заблокирован
        """
        rate_info = self._ip_requests.get(ip_address)
        if rate_info and rate_info.blocked_until:
            was_blocked = rate_info.is_blocked()
            rate_info.blocked_until = None
            if was_blocked:
                self.logger.info(f"IP {ip_address} разблокирован")
            return was_blocked
        return False

    def cleanup_expired(self) -> int:
        """
        Очистка старых записей

        Returns:
            int: Количество удаленных записей
        """
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)

        # Очищаем только если прошло достаточно времени с последней очистки
        if (now - self._last_cleanup).total_seconds() < 300:  # 5 минут
            return 0

        removed_count = 0
        for ip, rate_info in list(self._ip_requests.items()):

            # Удаляем запросы старше часа
            old_requests = [t for t in rate_info.requests if t < hour_ago]
            rate_info.requests = [
                t for t in rate_info.requests if t not in old_requests]

            # Если нет активности и не заблокирован - удаляем запись
            if not rate_info.requests and not rate_info.blocked_until:
                del self._ip_requests[ip]
                removed_count += 1

        self._last_cleanup = now
        return removed_count


# Глобальный экземпляр rate limiter
rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Получение глобального экземпляра rate limiter"""

    return rate_limiter


def check_rate_limit(ip_address: str) -> Tuple[bool, Dict]:
    """
    Проверка rate limit для IP
    """

    limiter = get_rate_limiter()
    is_allowed, remaining = limiter.is_allowed(ip_address)
    info = limiter.get_rate_limit_info(ip_address)
    return is_allowed, info
