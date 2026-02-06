"""Главный координатор безопасности
Обновлен для использования базового класса и новых утилит
"""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from security_service.account_locker import AccountLocker
from security_service.ip_blocker import IpBlocker
from security_service.rate_limiter import RateLimiter
from security_service.suspicious_detector import SuspiciousActivityDetector
from common.base_service import BaseService


class SecurityService(BaseService):
    """Главный координатор всех сервисов безопасности"""

    def __init__(self, config, db_session):
        super().__init__()
        self.config = config
        self.db_session = db_session

        # Инициализируем все сервисы безопасности
        self.account_locker = AccountLocker(config, db_session)
        self.ip_blocker = IpBlocker(config)
        self.rate_limiter = RateLimiter(config, db_session)
        self.suspicious_detector = SuspiciousActivityDetector(
            config, db_session)

    def check_security_status(
        self,
        email: str,
        ip_address: str,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """Комплексная проверка безопасности"""
        try:
            security_issues = []
            all_checks_passed = True

            # 1. Проверка лимитов запросов
            rate_limit_result = self.rate_limiter.check_rate_limit(
                ip_address=ip_address,
                email=email
            )

            if not rate_limit_result.get("success"):
                security_issues.append({
                    "type": "rate_limit",
                    "message": "Превышен лимит запросов",
                    "details": rate_limit_result.get("error")
                })
                all_checks_passed = False

            # 2. Проверка блокировки аккаунта
            is_locked, lock_message = self.account_locker.is_account_locked(
                email)
            if is_locked:
                security_issues.append({
                    "type": "account_locked",
                    "message": lock_message,
                    "details": {"email": email}
                })
                all_checks_passed = False

            # 3. Проверка блокировки IP
            is_ip_blocked, ip_block_message = self.ip_blocker.is_ip_blocked(
                ip_address)
            if is_ip_blocked:
                security_issues.append({
                    "type": "ip_blocked",
                    "message": ip_block_message,
                    "details": {"ip_address": ip_address}
                })
                all_checks_passed = False

            # 4. Анализ подозрительной активности
            suspicious_result = self.suspicious_detector.detect_suspicious_login(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )

            suspicious_data = suspicious_result.get("data", {})
            if suspicious_data.get("is_suspicious"):
                security_issues.append({
                    "type": "suspicious_activity",
                    "message": "Обнаружена подозрительная активность",
                    "details": {
                        "risk_level": suspicious_data.get("risk_level"),
                        "indicators": suspicious_data.get("indicators", []),
                        "recommendations": suspicious_data.get("recommendations", [])
                    }
                })
                all_checks_passed = False

            if all_checks_passed:
                return self._handle_success(
                    "Все проверки безопасности пройдены",
                    data={
                        "status": "secure",
                        "checks_passed": True,
                        "security_issues": []
                    }
                )
            else:
                return self._handle_success(
                    "Обнаружены проблемы безопасности",
                    data={
                        "status": "warning",
                        "checks_passed": False,
                        "security_issues": security_issues
                    }
                )

        except Exception as e:
            return self._handle_error(e, "комплексной проверки безопасности")

    def handle_failed_login(
        self,
        email: str,
        ip_address: str,
        user_agent: str = None,
        failure_reason: str = None
    ) -> Dict[str, Any]:
        """Обработка неудачной попытки входа"""
        try:
            actions_taken = []

            # 1. Проверяем количество неудачных попыток
            # В реальном приложении здесь была бы логика подсчета неудачных попыток

            # 2. Блокируем аккаунт при превышении лимита
            max_attempts = getattr(self.config, 'MAX_LOGIN_ATTEMPTS', 5)
            lock_duration = getattr(
                self.config, 'ACCOUNT_LOCK_DURATION', 30)  # минут

            # Заглушка для подсчета неудачных попыток
            # self._count_failed_attempts(email, ip_address)
            failed_attempts = 0

            if failed_attempts >= max_attempts:
                lock_result = self.account_locker.lock_account(
                    email=email,
                    duration_minutes=lock_duration,
                    reason=f"Превышен лимит неудачных попыток входа ({failed_attempts})"
                )

                if lock_result.get("success"):
                    actions_taken.append("Аккаунт заблокирован")

            # 3. Анализируем подозрительную активность
            suspicious_result = self.suspicious_detector.detect_suspicious_login(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )

            # 4. Блокируем IP при критическом уровне риска
            suspicious_data = suspicious_result.get("data", {})
            risk_level = suspicious_data.get("risk_level")

            if risk_level == "critical":
                ip_block_result = self.ip_blocker.block_ip_address(
                    ip_address=ip_address,
                    duration_hours=24,
                    reason="Критический уровень подозрительной активности"
                )

                if ip_block_result.get("success"):
                    actions_taken.append("IP адрес заблокирован")

            return self._handle_success(
                "Обработка неудачной попытки входа завершена",
                data={
                    "failed_attempts": failed_attempts,
                    "max_attempts": max_attempts,
                    "actions_taken": actions_taken,
                    "risk_assessment": {
                        "risk_level": risk_level,
                        "indicators": suspicious_data.get("indicators", []),
                        "recommendations": suspicious_data.get("recommendations", [])
                    }
                }
            )

        except Exception as e:
            return self._handle_error(e, "обработки неудачной попытки входа")

    def handle_successful_login(
        self,
        email: str,
        ip_address: str,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """Обработка успешного входа"""
        try:
            actions_taken = []

            # 1. Разблокировка аккаунта при успешном входе
            unlock_result = self.account_locker.unlock_account(email)
            if unlock_result.get("success"):
                actions_taken.append("Аккаунт разблокирован")

            # 2. Анализ входа на предмет безопасности
            suspicious_result = self.suspicious_detector.detect_suspicious_login(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )

            suspicious_data = suspicious_result.get("data", {})

            # 3. Логирование успешного входа
            # В реальном приложении здесь была бы запись в лог

            return self._handle_success(
                "Обработка успешного входа завершена",
                data={
                    "actions_taken": actions_taken,
                    "security_assessment": {
                        "risk_level": suspicious_data.get("risk_level"),
                        "indicators": suspicious_data.get("indicators", []),
                        "recommendations": suspicious_data.get("recommendations", [])
                    }
                }
            )

        except Exception as e:
            return self._handle_error(e, "обработки успешного входа")

    def get_security_status(self) -> Dict[str, Any]:
        """Получение общего статуса безопасности системы"""
        try:
            # Получаем статистику по всем компонентам
            # В реальном приложении здесь были бы запросы к БД

            security_status = {
                "overall_status": "operational",
                "components": {
                    "account_locker": {"status": "operational"},
                    "ip_blocker": {"status": "operational"},
                    "rate_limiter": {"status": "operational"},
                    "suspicious_detector": {"status": "operational"}
                },
                "last_updated": datetime.now().isoformat(),
                "note": "Детальная статистика требует реализации мониторинга"
            }

            return self._handle_success(
                "Статус безопасности системы получен",
                data=security_status
            )

        except Exception as e:
            return self._handle_error(e, "получения статуса безопасности")
