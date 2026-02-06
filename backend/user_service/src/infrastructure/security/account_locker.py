"""
Сервис для блокировки и разблокировки пользовательских аккаунтов
Мигрирован из старой архитектуры в новую Clean Architecture
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

from ...interfaces.user import UserRepositoryInterface
from ...infrastructure.common.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException
)


class AccountLocker:
    """Сервис для управления блокировкой аккаунтов пользователей"""

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        config: Optional[Dict[str, Any]] = None
    ):
        self.user_repository = user_repository
        self.config = config or {}
        self.default_lock_duration = self.config.get(
            'DEFAULT_LOCK_DURATION_MINUTES', 30)
        self.max_lock_duration = self.config.get(
            'MAX_LOCK_DURATION_MINUTES', 1440)  # 24 часа

    async def lock_account(
        self,
        email: str,
        duration_minutes: Optional[int] = None,
        reason: str = "Неудачные попытки входа"
    ) -> Dict[str, Any]:
        """
        Блокировка аккаунта пользователя

        Args:
            email: Email пользователя для блокировки
            duration_minutes: Длительность блокировки в минутах
            reason: Причина блокировки

        Returns:
            Dict с результатом операции
        """
        try:
            # Валидация входных параметров
            if not email:
                raise ValidationException(
                    "Email является обязательным параметром")

            # Поиск пользователя
            user = await self.user_repository.get_by_email(email)
            if not user:
                raise NotFoundException(
                    f"Пользователь с email {email} не найден")

            # Валидация длительности блокировки
            lock_duration = duration_minutes or self.default_lock_duration
            if lock_duration > self.max_lock_duration:
                lock_duration = self.max_lock_duration

            # Расчет времени разблокировки
            unlock_time = datetime.utcnow() + timedelta(minutes=lock_duration)

            # Обновление пользователя
            update_data = {
                "is_locked": True,
                "locked_until": unlock_time,
                "lock_reason": reason,
                "updated_at": datetime.utcnow()
            }

            await self.user_repository.update(user.id, update_data)

            return {
                "success": True,
                "message": (
                    f"Аккаунт {email} заблокирован до "
                    f"{unlock_time.strftime('%Y-%m-%d %H:%M:%S')}"
                ),
                "data": {
                    "email": email,
                    "locked_until": unlock_time.isoformat(),
                    "duration_minutes": lock_duration,
                    "reason": reason
                }
            }

        except (NotFoundException, ValidationException) as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": type(e).__name__
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при блокировке аккаунта: {str(e)}")

    async def unlock_account(self, email: str) -> Dict[str, Any]:
        """
        Разблокировка аккаунта пользователя

        Args:
            email: Email пользователя для разблокировки

        Returns:
            Dict с результатом операции
        """
        try:
            if not email:
                raise ValidationException(
                    "Email является обязательным параметром")

            # Поиск пользователя
            user = await self.user_repository.get_by_email(email)
            if not user:
                raise NotFoundException(
                    f"Пользователь с email {email} не найден")

            # Обновление пользователя
            update_data = {
                "is_locked": False,
                "locked_until": None,
                "lock_reason": None,
                "updated_at": datetime.utcnow()
            }

            await self.user_repository.update(user.id, update_data)

            return {
                "success": True,
                "message": f"Аккаунт {email} разблокирован",
                "data": {
                    "email": email,
                    "unlocked_at": datetime.utcnow().isoformat()
                }
            }

        except (NotFoundException, ValidationException) as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": type(e).__name__
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при разблокировке аккаунта: {str(e)}")

    async def is_account_locked(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Проверка блокировки аккаунта

        Args:
            email: Email пользователя

        Returns:
            Tuple[bool, Optional[str]]: (заблокирован, сообщение)
        """
        try:
            if not email:
                return False, None

            # Поиск пользователя
            user = await self.user_repository.get_by_email(email)
            if not user:
                return False, None

            # Проверка статуса блокировки
            if user.is_locked and user.locked_until:
                if datetime.utcnow() < user.locked_until:
                    remaining_time = user.locked_until - datetime.utcnow()
                    minutes_remaining = int(
                        remaining_time.total_seconds() / 60)
                    return True, f"Аккаунт заблокирован. Осталось {minutes_remaining} минут"
                else:
                    # Время блокировки истекло, автоматически разблокируем
                    await self.unlock_account(email)
                    return False, None

            return False, None

        except Exception as e:
            # Логирование ошибки, но не прерываем выполнение
            return False, f"Ошибка проверки статуса аккаунта: {str(e)}"

    async def get_locked_accounts(self, limit: int = 100) -> Dict[str, Any]:
        """
        Получение списка заблокированных аккаунтов

        Args:
            limit: Максимальное количество записей

        Returns:
            Dict со списком заблокированных аккаунтов
        """
        try:
            # Получаем всех заблокированных пользователей
            users = await self.user_repository.get_locked_users(limit=limit)

            locked_accounts = []
            for user in users:
                locked_accounts.append({
                    "id": str(user.id),
                    "email": user.email,
                    "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                    "lock_reason": user.lock_reason,
                    "created_at": user.created_at.isoformat()
                })

            return {
                "success": True,
                "data": {
                    "locked_accounts": locked_accounts,
                    "total": len(locked_accounts)
                }
            }

        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении списка заблокированных аккаунтов: {str(e)}")

    async def auto_unlock_expired(self) -> Dict[str, Any]:
        """
        Автоматическая разблокировка аккаунтов с истекшим временем блокировки

        Returns:
            Dict с результатом операции
        """
        try:
            # Получаем пользователей с истекшей блокировкой
            expired_users = await self.user_repository.get_expired_locked_users()

            unlocked_count = 0
            for user in expired_users:
                await self.unlock_account(user.email)
                unlocked_count += 1

            return {
                "success": True,
                "message": f"Автоматически разблокировано {unlocked_count} аккаунтов",
                "data": {
                    "unlocked_count": unlocked_count,
                    "processed_at": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            raise DatabaseException(
                f"Ошибка при автоматической разблокировке: {str(e)}")

    async def get_account_status(self, email: str) -> Dict[str, Any]:
        """
        Получение детального статуса аккаунта

        Args:
            email: Email пользователя

        Returns:
            Dict с детальной информацией о статусе
        """
        try:
            user = await self.user_repository.get_by_email(email)
            if not user:
                raise NotFoundException(
                    f"Пользователь с email {email} не найден")

            is_locked, lock_message = await self.is_account_locked(email)

            status = {
                "email": user.email,
                "is_active": user.is_active,
                "is_locked": is_locked,
                "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                "lock_reason": user.lock_reason,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
                "lock_message": lock_message
            }

            return {
                "success": True,
                "data": status
            }

        except NotFoundException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "USER_NOT_FOUND"
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении статуса аккаунта: {str(e)}")
