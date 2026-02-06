"""Класс AccountLocker для блокировки и разблокировки аккаунтов
Обновлен для использования базового класса
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.user_service.src.models import User
from common.base_service import BaseService


logger = logging.getLogger(__name__)


class AccountLocker(BaseService):
    """Класс для управления блокировкой аккаунтов"""

    def __init__(self, config, db_session: Session):
        super().__init__()
        self.config = config
        self.db_session = db_session

    def lock_account(
        self,
        email: str,
        duration_minutes: int = 30,
        reason: str = "Неудачные попытки входа"
    ) -> dict:
        """Блокировка аккаунта"""
        try:
            # Ищем пользователя
            user = self.db_session.query(User).filter(
                User.email == email).first()

            if not user:
                return self._handle_error(
                    Exception(f"Пользователь с email {email} не найден"),
                    "блокировки аккаунта"
                )

            # Устанавливаем время разблокировки
            unlock_time = datetime.now() + timedelta(minutes=duration_minutes)

            # Обновляем пользователя
            user.is_locked = True
            user.locked_until = unlock_time
            user.lock_reason = reason
            user.updated_at = datetime.now()

            self.db_session.commit()

            return self._handle_success(
                f"Аккаунт {email} заблокирован до {unlock_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        except SQLAlchemyError as e:
            self.db_session.rollback()
            return self._handle_error(e, "блокировки аккаунта")

    def unlock_account(self, email: str) -> dict:
        """Разблокировка аккаунта"""
        try:
            # Ищем пользователя
            user = self.db_session.query(User).filter(
                User.email == email).first()

            if not user:
                return self._handle_error(
                    Exception(f"Пользователь с email {email} не найден"),
                    "разблокировки аккаунта"
                )

            # Разблокируем пользователя
            user.is_locked = False
            user.locked_until = None
            user.lock_reason = None
            user.updated_at = datetime.now()

            self.db_session.commit()

            return self._handle_success(f"Аккаунт {email} разблокирован")

        except SQLAlchemyError as e:
            self.db_session.rollback()
            return self._handle_error(e, "разблокировки аккаунта")

    def is_account_locked(self, email: str) -> Tuple[bool, Optional[str]]:
        """Проверка, заблокирован ли аккаунт"""
        try:
            user = self.db_session.query(User).filter(
                User.email == email).first()

            if not user:
                return False, None

            # Проверяем, заблокирован ли аккаунт
            if user.is_locked and user.locked_until:
                if datetime.now() < user.locked_until:
                    remaining_time = user.locked_until - datetime.now()
                    minutes_remaining = int(
                        remaining_time.total_seconds() / 60)
                    return True, f"Аккаунт заблокирован. Осталось {minutes_remaining} минут"
                else:
                    # Время блокировки истекло, автоматически разблокируем
                    self.unlock_account(email)
                    return False, None

            return False, None

        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при проверке блокировки аккаунта {email}: {e}")
            return False, "Ошибка проверки статуса аккаунта"
