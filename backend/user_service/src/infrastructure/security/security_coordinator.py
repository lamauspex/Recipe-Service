"""
Координатор безопасности - объединяет все компоненты безопасности
Мигрирован из старого SecurityService в новую Clean Architecture
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .account_locker import AccountLocker
from .ip_blocker import IpBlocker
from .rate_limiter import RateLimiter
from .suspicious_activity_detector import SuspiciousActivityDetector
from ...interfaces.user import UserRepositoryInterface
from ...interfaces.security import SecurityInterface
from ...infrastructure.common.exceptions import ValidationException


class SecurityCoordinator(SecurityInterface):
    """
    Координатор безопасности, объединяющий все сервисы безопасности
    Заменяет старый SecurityService
    """

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        security_service: SecurityInterface,
        config: Optional[Dict[str, Any]] = None
    ):
        self.user_repository = user_repository
        self.security_service = security_service
        self.config = config or {}

        # Инициализация компонентов безопасности
        self.account_locker = AccountLocker(user_repository, config)
        self.ip_blocker = IpBlocker(config)
        self.rate_limiter = RateLimiter(config)
        self.suspicious_detector = SuspiciousActivityDetector(
            user_repository, config)

    # === Адаптеры для совместимости с SecurityInterface ===

    async def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return await self.security_service.hash_password(password)

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return await self.security_service.verify_password(password, hashed_password)

    async def generate_access_token(self, user_data: Dict[str, Any]) -> str:
        """Генерация access токена"""
        return await self.security_service.generate_access_token(user_data)

    async def generate_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Генерация refresh токена"""
        return await self.security_service.generate_refresh_token(user_data)

    async def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка access токена"""
        return await self.security_service.verify_access_token(token)

    async def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка refresh токена"""
        return await self.security_service.verify_refresh_token(token)

    async def revoke_token(self, token: str) -> bool:
        """Отзыв токена"""
        return await self.security_service.revoke_token(token)

    async def generate_password_reset_token(self, user_email: str) -> str:
        """Генерация токена для сброса пароля"""
        return await self.security_service.generate_password_reset_token(user_email)

    async def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Проверка токена для сброса пароля"""
        return await self.security_service.verify_password_reset_token(token)

    # === Расширенная функциональность безопасности ===

    async def comprehensive_security_check(
        self,
        email: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        action: str = "login"
    ) -> Dict[str, Any]:
        """
        Комплексная проверка безопасности для операции входа

        Args:
            email: Email пользователя
            ip_address: IP адрес клиента
            user_agent: User Agent клиента
            action: Тип операции (login, register, password_reset)

        Returns:
            Dict с результатами всех проверок безопасности
        """
        try:
            security_results = {
                "timestamp": datetime.utcnow().isoformat(),
                "email": email,
                "ip_address": ip_address,
                "action": action,
                "overall_status": "allowed",
                "checks": {}
            }

            # 1. Проверка блокировки аккаунта
            is_locked, lock_message = await self.account_locker.is_account_locked(email)
            security_results["checks"]["account_lock"] = {
                "status": "blocked" if is_locked else "clear",
                "message": lock_message,
                "allowed": not is_locked
            }

            if is_locked:
                security_results["overall_status"] = "blocked"
                security_results["block_reason"] = lock_message
                return security_results

            # 2. Проверка блокировки IP
            ip_status = await self.ip_blocker.is_ip_blocked(ip_address)
            security_results["checks"]["ip_block"] = {
                "status": "blocked" if ip_status["is_blocked"] else "clear",
                "message": ip_status.get("reason"),
                "allowed": not ip_status["is_blocked"]
            }

            if ip_status["is_blocked"]:
                security_results["overall_status"] = "blocked"
                security_results["block_reason"] = ip_status.get(
                    "reason", "IP адрес заблокирован")
                return security_results

            # 3. Проверка rate limit
            rate_limit_result = await self.rate_limiter.check_rate_limit(
                identifier=email,
                action=action,
                ip_address=ip_address
            )
            security_results["checks"]["rate_limit"] = {
                "status": "limited" if not rate_limit_result["success"] else "clear",
                "message": rate_limit_result.get("reason", "OK"),
                "allowed": rate_limit_result["success"],
                "details": rate_limit_result
            }

            if not rate_limit_result["success"]:
                security_results["overall_status"] = "limited"
                security_results["limit_reason"] = rate_limit_result.get(
                    "reason")
                return security_results

            # 4. Анализ подозрительной активности
            suspicious_result = await self.suspicious_detector.detect_suspicious_login(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )

            if suspicious_result["success"]:
                analysis = suspicious_result["data"]
                security_results["checks"]["suspicious_activity"] = {
                    "status": "suspicious" if analysis["is_suspicious"] else "clear",
                    "risk_level": analysis["risk_level"],
                    "risk_score": analysis["risk_score"],
                    "allowed": True,  # Не блокируем, только предупреждаем
                    "indicators": analysis["indicators"],
                    "recommendations": analysis["recommendations"]
                }

                # Если риск критический, требуем дополнительной проверки
                if analysis["risk_level"] == "critical":
                    security_results["overall_status"] = "requires_verification"
                    security_results["verification_required"] = True
                    security_results["verification_reasons"] = analysis["recommendations"]
                elif analysis["risk_level"] == "high":
                    security_results["overall_status"] = "requires_monitoring"
                    security_results["monitoring_required"] = True

            return security_results

        except Exception as e:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "email": email,
                "ip_address": ip_address,
                "action": action,
                "overall_status": "error",
                "error": str(e),
                "allowed": False
            }

    async def handle_security_violation(
        self,
        email: str,
        ip_address: str,
        violation_type: str,
        severity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Обработка нарушения безопасности

        Args:
            email: Email пользователя
            ip_address: IP адрес клиента
            violation_type: Тип нарушения
            severity: Серьезность нарушения

        Returns:
            Dict с результатами действий по безопасности
        """
        try:
            actions_taken = []

            # Определяем меры в зависимости от типа нарушения и серьезности
            if violation_type == "failed_login" and severity in ["high", "critical"]:
                # Блокируем аккаунт
                lock_result = await self.account_locker.lock_account(
                    email=email,
                    duration_minutes=60 if severity == "high" else 1440,  # 1 час или 1 день
                    reason=f"Множественные неудачные попытки входа (серьезность: {severity})"
                )
                actions_taken.append(("account_lock", lock_result))

            if violation_type in ["rapid_attempts", "brute_force"] and severity in ["medium", "high", "critical"]:
                # Блокируем IP
                block_duration = 24 if severity == "critical" else (
                    6 if severity == "high" else 2)
                ip_result = await self.ip_blocker.block_ip_address(
                    ip_address=ip_address,
                    duration_hours=block_duration,
                    reason=f"Подозрительная активность: {violation_type} (серьезность: {severity})"
                )
                actions_taken.append(("ip_block", ip_result))

            if violation_type in ["suspicious_login", "unusual_activity"] and severity == "critical":
                # Временно блокируем доступ
                limit_result = await self.rate_limiter.check_rate_limit(
                    identifier=email,
                    action="login",
                    ip_address=ip_address
                )
                actions_taken.append(("rate_limit", limit_result))

            # Автоматическая очистка устаревших данных
            cleanup_result = await self._cleanup_security_data()
            actions_taken.append(("cleanup", cleanup_result))

            return {
                "success": True,
                "violation_type": violation_type,
                "severity": severity,
                "actions_taken": actions_taken,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "violation_type": violation_type,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_security_status(self, email: Optional[str] = None) -> Dict[str, Any]:
        """
        Получение общего статуса безопасности

        Args:
            email: Email пользователя (опционально)

        Returns:
            Dict с общим статусом безопасности
        """
        try:
            status = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_email": email,
                "components": {}
            }

            # Статус компонентов безопасности
            if email:
                # Статус конкретного пользователя
                is_locked, lock_message = await self.account_locker.is_account_locked(email)
                status["components"]["account_lock"] = {
                    "is_locked": is_locked,
                    "message": lock_message
                }

                rate_status = await self.rate_limiter.get_rate_limit_status(email, "login")
                status["components"]["rate_limit"] = rate_status["data"] if rate_status["success"] else None

                # История подозрительной активности
                history_result = await self.suspicious_detector.get_login_history(email, days=7)
                status["components"]["activity_history"] = history_result["data"] if history_result["success"] else None

            # Общая статистика
            blocked_ips_result = await self.ip_blocker.get_blocked_ips(limit=10)
            status["components"]["blocked_ips"] = blocked_ips_result["data"] if blocked_ips_result["success"] else None

            # Статистика заблокированных аккаунтов
            locked_accounts_result = await self.account_locker.get_locked_accounts(limit=10)
            status["components"]["locked_accounts"] = locked_accounts_result["data"] if locked_accounts_result["success"] else None

            return {
                "success": True,
                "data": status
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def reset_security_flags(
        self,
        email: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Сброс флагов безопасности

        Args:
            email: Email пользователя (опционально)
            ip_address: IP адрес (опционально)

        Returns:
            Dict с результатами сброса
        """
        try:
            actions = []

            if email:
                # Сброс лимитов для пользователя
                reset_result = await self.rate_limiter.reset_rate_limit(email)
                actions.append(("user_rate_limit", reset_result))

                # Разблокировка аккаунта
                unlock_result = await self.account_locker.unlock_account(email)
                actions.append(("account_unlock", unlock_result))

            if ip_address:
                # Разблокировка IP
                unblock_result = await self.ip_blocker.unblock_ip_address(ip_address)
                actions.append(("ip_unblock", unblock_result))

            return {
                "success": True,
                "actions": actions,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _cleanup_security_data(self) -> Dict[str, Any]:
        """Очистка устаревших данных безопасности"""
        try:
            cleanup_results = []

            # Очистка rate limiter
            rate_cleanup = await self.rate_limiter.cleanup_expired_data()
            cleanup_results.append(("rate_limiter", rate_cleanup))

            # Автоматическая разблокировка истекших блокировок
            ip_cleanup = await self.ip_blocker.auto_unblock_expired()
            cleanup_results.append(("ip_blocker", ip_cleanup))

            account_cleanup = await self.account_locker.auto_unlock_expired()
            cleanup_results.append(("account_locker", account_cleanup))

            return {
                "success": True,
                "cleanup_results": cleanup_results,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
