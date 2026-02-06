"""
Расширенный сервис для rate limiting
Мигрирован из старой архитектуры в новую Clean Architecture
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from collections import defaultdict, deque
import time

from ...infrastructure.common.exceptions import (
    ValidationException,
    DatabaseException
)


class RateLimiter:
    """Расширенный сервис для управления rate limiting"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Конфигурация лимитов
        self.default_limits = {
            "login": {
                "requests_per_minute": 5,
                "requests_per_hour": 100,
                "requests_per_day": 1000
            },
            "register": {
                "requests_per_hour": 3,
                "requests_per_day": 10
            },
            "password_reset": {
                "requests_per_hour": 3,
                "requests_per_day": 5
            },
            "api_general": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "requests_per_day": 10000
            }
        }

        # Хранилище счетчиков (в реальном приложении - Redis/БД)
        self._rate_limiters: Dict[str, Dict[str, deque]
                                  ] = defaultdict(lambda: defaultdict(deque))

        # Кэш для временных блокировок
        self._temp_blocks: Dict[str, Dict[str, Any]] = {}

    async def check_rate_limit(
        self,
        identifier: str,
        action: str = "api_general",
        ip_address: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Проверка rate limit для идентификатора

        Args:
            identifier: Идентификатор (IP, email, user_id)
            action: Тип действия (login, register, api_general)
            ip_address: IP адрес клиента
            email: Email пользователя

        Returns:
            Dict с результатом проверки
        """
        try:
            if not identifier:
                raise ValidationException(
                    "Identifier является обязательным параметром")

            # Получаем лимиты для действия
            limits = self.config.get(f"{action}_limits", self.default_limits.get(
                action, self.default_limits["api_general"]))

            # Проверяем временную блокировку
            temp_block = self._check_temp_block(identifier)
            if temp_block:
                return {
                    "success": False,
                    "blocked": True,
                    "remaining_time": temp_block["remaining_time"],
                    "reason": temp_block["reason"],
                    "retry_after": temp_block["retry_after"]
                }

            # Проверяем различные временные окна
            violations = []
            current_time = time.time()

            # Проверка по минутам
            if "requests_per_minute" in limits:
                minute_violation = await self._check_time_window(
                    identifier, action, "minute", 60, limits["requests_per_minute"], current_time
                )
                if minute_violation:
                    violations.append(minute_violation)

            # Проверка по часам
            if "requests_per_hour" in limits:
                hour_violation = await self._check_time_window(
                    identifier, action, "hour", 3600, limits["requests_per_hour"], current_time
                )
                if hour_violation:
                    violations.append(hour_violation)

            # Проверка по дням
            if "requests_per_day" in limits:
                day_violation = await self._check_time_window(
                    identifier, action, "day", 86400, limits["requests_per_day"], current_time
                )
                if day_violation:
                    violations.append(day_violation)

            # Добавляем текущий запрос в счетчик
            await self._record_request(identifier, action, current_time)

            # Если есть нарушения, применяем соответствующие меры
            if violations:
                return await self._handle_rate_limit_violation(identifier, action, violations, ip_address, email)

            # Все ок, возвращаем информацию о лимитах
            return {
                "success": True,
                "blocked": False,
                "limits": {
                    "requests_per_minute": limits.get("requests_per_minute"),
                    "requests_per_hour": limits.get("requests_per_hour"),
                    "requests_per_day": limits.get("requests_per_day")
                },
                "remaining": await self._get_remaining_requests(identifier, action, limits)
            }

        except ValidationException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "INVALID_IDENTIFIER"
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при проверке rate limit: {str(e)}")

    async def get_rate_limit_status(self, identifier: str, action: str = "api_general") -> Dict[str, Any]:
        """
        Получение статуса rate limit для идентификатора

        Args:
            identifier: Идентификатор
            action: Тип действия

        Returns:
            Dict с текущим статусом
        """
        try:
            if not identifier:
                raise ValidationException(
                    "Identifier является обязательным параметром")

            limits = self.config.get(f"{action}_limits", self.default_limits.get(
                action, self.default_limits["api_general"]))
            current_time = time.time()

            # Получаем текущие счетчики
            minute_count = await self._get_request_count(identifier, action, "minute", 60, current_time)
            hour_count = await self._get_request_count(identifier, action, "hour", 3600, current_time)
            day_count = await self._get_request_count(identifier, action, "day", 86400, current_time)

            return {
                "success": True,
                "data": {
                    "identifier": identifier,
                    "action": action,
                    "current_usage": {
                        "minute": minute_count,
                        "hour": hour_count,
                        "day": day_count
                    },
                    "limits": limits,
                    "remaining": {
                        "minute": max(0, limits.get("requests_per_minute", 0) - minute_count),
                        "hour": max(0, limits.get("requests_per_hour", 0) - hour_count),
                        "day": max(0, limits.get("requests_per_day", 0) - day_count)
                    },
                    "reset_times": {
                        "minute": current_time + 60,
                        "hour": current_time + 3600,
                        "day": current_time + 86400
                    }
                }
            }

        except ValidationException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "INVALID_IDENTIFIER"
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении статуса rate limit: {str(e)}")

    async def reset_rate_limit(self, identifier: str, action: Optional[str] = None) -> Dict[str, Any]:
        """
        Сброс rate limit для идентификатора

        Args:
            identifier: Идентификатор
            action: Тип действия (None для всех действий)

        Returns:
            Dict с результатом операции
        """
        try:
            if not identifier:
                raise ValidationException(
                    "Identifier является обязательным параметром")

            reset_count = 0

            if action:
                # Сброс конкретного действия
                if identifier in self._rate_limiters and action in self._rate_limiters[identifier]:
                    self._rate_limiters[identifier][action].clear()
                    reset_count = 1
            else:
                # Сброс всех действий для идентификатора
                if identifier in self._rate_limiters:
                    for action_key in self._rate_limiters[identifier]:
                        self._rate_limiters[identifier][action_key].clear()
                    reset_count = len(self._rate_limiters[identifier])

            # Сброс временных блокировок
            if identifier in self._temp_blocks:
                del self._temp_blocks[identifier]

            return {
                "success": True,
                "message": f"Rate limit сброшен для {identifier}",
                "data": {
                    "identifier": identifier,
                    "action": action,
                    "reset_count": reset_count,
                    "reset_at": datetime.utcnow().isoformat()
                }
            }

        except ValidationException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "INVALID_IDENTIFIER"
            }
        except Exception as e:
            raise DatabaseException(f"Ошибка при сбросе rate limit: {str(e)}")

    async def _check_time_window(
        self,
        identifier: str,
        action: str,
        window_type: str,
        window_seconds: int,
        limit: int,
        current_time: float
    ) -> Optional[Dict[str, Any]]:
        """Проверка лимита для временного окна"""
        key = f"{identifier}_{action}_{window_type}"

        # Удаляем устаревшие записи
        cutoff_time = current_time - window_seconds
        window_requests = self._rate_limiters[key]

        while window_requests and window_requests[0] < cutoff_time:
            window_requests.popleft()

        if len(window_requests) >= limit:
            return {
                "window_type": window_type,
                "window_seconds": window_seconds,
                "current_count": len(window_requests),
                "limit": limit,
                "reset_time": current_time + window_seconds
            }

        return None

    async def _record_request(self, identifier: str, action: str, current_time: float):
        """Запись запроса в счетчик"""
        for window_type, window_seconds in [("minute", 60), ("hour", 3600), ("day", 86400)]:
            key = f"{identifier}_{action}_{window_type}"
            self._rate_limiters[key].append(current_time)

    async def _get_request_count(
        self,
        identifier: str,
        action: str,
        window_type: str,
        window_seconds: int,
        current_time: float
    ) -> int:
        """Получение количества запросов в окне"""
        key = f"{identifier}_{action}_{window_type}"
        cutoff_time = current_time - window_seconds

        window_requests = self._rate_limiters[key]
        while window_requests and window_requests[0] < cutoff_time:
            window_requests.popleft()

        return len(window_requests)

    async def _get_remaining_requests(self, identifier: str, action: str, limits: Dict[str, int]) -> Dict[str, int]:
        """Получение оставшихся запросов"""
        current_time = time.time()
        remaining = {}

        for window_type, window_seconds in [("minute", 60), ("hour", 3600), ("day", 86400)]:
            limit_key = f"requests_per_{window_type}"
            if limit_key in limits:
                current_count = await self._get_request_count(identifier, action, window_type, window_seconds, current_time)
                remaining[window_type] = max(
                    0, limits[limit_key] - current_count)

        return remaining

    def _check_temp_block(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Проверка временной блокировки"""
        if identifier in self._temp_blocks:
            block_info = self._temp_blocks[identifier]
            if datetime.utcnow() < block_info["expires_at"]:
                remaining_time = block_info["expires_at"] - datetime.utcnow()
                return {
                    "remaining_time": remaining_time.total_seconds(),
                    "retry_after": int(remaining_time.total_seconds()),
                    "reason": block_info["reason"]
                }
            else:
                # Блокировка истекла, удаляем
                del self._temp_blocks[identifier]

        return None

    async def _handle_rate_limit_violation(
        self,
        identifier: str,
        action: str,
        violations: List[Dict[str, Any]],
        ip_address: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Обработка нарушения rate limit"""
        # Определяем серьезность нарушения
        max_violation = max(
            violations, key=lambda v: v["current_count"] / v["limit"])

        # Рассчитываем время блокировки
        violation_ratio = max_violation["current_count"] / \
            max_violation["limit"]

        if violation_ratio >= 2.0:  # Превышение в 2+ раза
            block_duration = 3600  # 1 час
            reason = "Значительное превышение лимита запросов"
        elif violation_ratio >= 1.5:  # Превышение в 1.5+ раза
            block_duration = 1800  # 30 минут
            reason = "Превышение лимита запросов"
        else:
            block_duration = 300  # 5 минут
            reason = "Превышение лимита запросов"

        # Устанавливаем временную блокировку
        expires_at = datetime.utcnow() + timedelta(seconds=block_duration)
        self._temp_blocks[identifier] = {
            "reason": reason,
            "expires_at": expires_at,
            "violations": violations
        }

        return {
            "success": False,
            "blocked": True,
            "remaining_time": block_duration,
            "reason": reason,
            "retry_after": block_duration,
            "violations": violations
        }

    async def cleanup_expired_data(self) -> Dict[str, Any]:
        """Очистка устаревших данных"""
        try:
            current_time = time.time()
            cleaned_count = 0

            # Очистка устаревших записей в rate limiters
            for key in list(self._rate_limiters.keys()):
                # Определяем максимальное время хранения (24 часа)
                cutoff_time = current_time - 86400

                # Очищаем старые записи
                window_requests = self._rate_limiters[key]
                while window_requests and window_requests[0] < cutoff_time:
                    window_requests.popleft()

                # Если нет активных записей, удаляем ключ
                if not window_requests:
                    del self._rate_limiters[key]
                    cleaned_count += 1

            # Очистка истекших временных блокировок
            expired_blocks = []
            for identifier in list(self._temp_blocks.keys()):
                if datetime.utcnow() >= self._temp_blocks[identifier]["expires_at"]:
                    expired_blocks.append(identifier)

            for identifier in expired_blocks:
                del self._temp_blocks[identifier]

            return {
                "success": True,
                "message": f"Очищено {cleaned_count} устаревших записей и {len(expired_blocks)} истекших блокировок",
                "data": {
                    "cleaned_rate_limiters": cleaned_count,
                    "cleaned_temp_blocks": len(expired_blocks),
                    "cleanup_time": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            raise DatabaseException(f"Ошибка при очистке данных: {str(e)}")
