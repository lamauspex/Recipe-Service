"""
Сервис безопасности
Интегрирует функциональность из старой архитектуры
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from ..common.password_utility import PasswordUtility


class SecurityService:
    """Сервис безопасности, объединяющий все аспекты безопасности"""

    def __init__(
        self,
        user_repository=None,
        role_repository=None,
        jwt_service=None,
        password_utility=None,
        rate_limit_utility=None
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.jwt_service = jwt_service
        self.password_utility = password_utility or PasswordUtility()
        self.rate_limit_utility = rate_limit_utility

    # === Работа с паролями ===

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self.password_utility.verify_password(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return self.password_utility.hash_password(password)

    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """Проверка сложности пароля"""
        return self.password_utility.validate_password_strength(password)

    # === Работа с токенами ===

    async def generate_access_token(self, user_data: Dict[str, Any]) -> str:
        """Генерация access токена"""
        if not self.jwt_service:
            return "mock_access_token"

        token_data = {
            "sub": user_data.get("user_id"),
            "email": user_data.get("email"),
            "role": user_data.get("role", "user")
        }
        return self.jwt_service.create_access_token(token_data)

    async def generate_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Генерация refresh токена"""
        if not self.jwt_service:
            return "mock_refresh_token"

        token_data = {
            "sub": user_data.get("user_id"),
            "email": user_data.get("email"),
            "role": user_data.get("role", "user")
        }
        return self.jwt_service.create_refresh_token(token_data)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка токена"""
        if not self.jwt_service:
            return {"sub": "mock_user_id", "email": "mock@example.com"}
        return self.jwt_service.decode_token(token)

    def is_token_expired(self, token: str) -> bool:
        """Проверка истечения токена"""
        if not self.jwt_service:
            return False
        return self.jwt_service.is_token_expired(token)

    def extract_user_id_from_token(self, token: str) -> Optional[str]:
        """Извлечение ID пользователя из токена"""
        if not self.jwt_service:
            return "mock_user_id"
        return self.jwt_service.extract_user_id(token)

    # === Работа с лимитами ===

    async def check_rate_limit(self, email: str = None, ip_address: str = None) -> Tuple[bool, Optional[str]]:
        """Проверка лимитов запросов"""
        if self.rate_limit_utility:
            return await self.rate_limit_utility.check_rate_limit(email, ip_address)
        return True, None

    # === Проверки безопасности ===

    async def authenticate_user(self, email: str, password: str) -> Tuple[bool, Optional[str]]:
        """Аутентификация пользователя"""
        try:
            if not self.user_repository:
                return True, None  # Mock для тестирования

            # Поиск пользователя
            user = await self.user_repository.get_by_email(email)
            if not user:
                return False, "Invalid email or password"

            # Проверка блокировки
            if user.is_locked and user.locked_until and user.locked_until > datetime.utcnow():
                return False, "Account is locked"

            # Проверка активности
            if not user.is_active:
                return False, "Account is deactivated"

            # Проверка пароля
            if not self.verify_password(password, user.hashed_password):
                return False, "Invalid email or password"

            return True, None

        except Exception as e:
            return False, f"Authentication failed: {str(e)}"

    async def check_user_permission(self, user_id: str, permission: str) -> bool:
        """Проверка разрешения пользователя"""
        try:
            if not self.user_repository:
                return True  # Mock для тестирования

            user = await self.user_repository.get_by_id(user_id)
            if not user:
                return False

            # Проверяем разрешения через роли
            user_roles = await self.user_repository.get_user_roles(user_id)

            for role in user_roles:
                # Проверяем разрешения роли (заглушка)
                role_permissions = await self._get_role_permissions(role.id)
                if permission in role_permissions:
                    return True

            return False

        except Exception:
            return False

    async def lock_user_account(
        self,
        user_id: str,
        reason: str = "Security violation",
        duration_hours: int = 24
    ) -> bool:
        """Блокировка аккаунта пользователя"""
        try:
            if not self.user_repository:
                return True  # Mock для тестирования

            lock_until = datetime.utcnow() + timedelta(hours=duration_hours)
            update_data = {
                "is_locked": True,
                "locked_until": lock_until,
                "lock_reason": reason
            }

            updated_user = await self.user_repository.update(user_id, update_data)
            return updated_user is not None

        except Exception:
            return False

    async def unlock_user_account(self, user_id: str) -> bool:
        """Разблокировка аккаунта пользователя"""
        try:
            if not self.user_repository:
                return True  # Mock для тестирования

            update_data = {
                "is_locked": False,
                "locked_until": None,
                "lock_reason": None
            }

            updated_user = await self.user_repository.update(user_id, update_data)
            return updated_user is not None

        except Exception:
            return False

    async def _get_role_permissions(self, role_id: str) -> list:
        """Получение разрешений роли (заглушка)"""
        # Заглушка - в реальной реализации здесь был бы запрос к БД
        return ["read", "write"]

    # === Комплексные проверки безопасности ===

    async def comprehensive_security_check(
        self,
        email: str = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """Комплексная проверка безопасности"""
        try:
            security_issues = []
            all_checks_passed = True

            # 1. Проверка лимитов
            rate_limit_ok, rate_limit_msg = await self.check_rate_limit(email, ip_address)
            if not rate_limit_ok:
                security_issues.append({
                    "type": "rate_limit",
                    "message": rate_limit_msg,
                    "severity": "high"
                })
                all_checks_passed = False

            # 2. Проверка блокировки пользователя
            if email and self.user_repository:
                user = await self.user_repository.get_by_email(email)
                if user and user.is_locked:
                    security_issues.append({
                        "type": "account_locked",
                        "message": "Account is locked",
                        "severity": "critical",
                        "details": {
                            "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                            "reason": user.lock_reason
                        }
                    })
                    all_checks_passed = False

            # 3. Проверка подозрительной активности (заглушка)
            suspicious_check = await self._check_suspicious_activity(email, ip_address, user_agent)
            if suspicious_check["is_suspicious"]:
                security_issues.append({
                    "type": "suspicious_activity",
                    "message": "Suspicious activity detected",
                    "severity": suspicious_check["severity"],
                    "details": suspicious_check["details"]
                })
                all_checks_passed = False

            return {
                "status": "secure" if all_checks_passed else "warning",
                "checks_passed": all_checks_passed,
                "security_issues": security_issues,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "status": "error",
                "checks_passed": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _check_suspicious_activity(
        self,
        email: str = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """Проверка подозрительной активности (заглушка)"""
        # Заглушка - в реальной реализации здесь был бы анализ паттернов
        return {
            "is_suspicious": False,
            "severity": "low",
            "details": {
                "indicators": [],
                "recommendations": []
            }
        }
