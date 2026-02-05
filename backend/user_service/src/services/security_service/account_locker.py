"""Класс AccountLocker для блокировки и разблокировки аккаунтов"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError

from backend.user_service.src.models import User


logger = logging.getLogger(__name__)


class AccountLocker:
    """Класс для управления блокировкой аккаунтов"""

    def __init__(self, config, db_session: Session):
        self.config = config
        self.db_session = db_session

    def lock_account(
        self,
        email: str,
        duration_minutes: int = 30,
        reason: str = "Неудачные попытки входа"
    ) -> dict:
        """Блокировка аккаунта - возвращает готовый ответ"""

        try:
            # Ищем пользователя
            user = self.db_session.query(User).filter(
                User.email == email
            ).first()

            if not user:
                return {
                    "error": f"Пользователь с email {email} не найден",
                    "success": False
                }

            # Устанавливаем время разблокировки
            unlock_time = datetime.now() + timedelta(minutes=duration_minutes)

            # Обновляем пользователя
            user.is_locked = True
            user.locked_until = unlock_time
            user.lock_reason = reason
            user.updated_at = datetime.now()

            self.db_session.commit()

            return {
                "message": f"Аккаунт {email} заблокирован до {unlock_time.strftime('%Y-%m-%d %H:%M:%S')}",
                "success": True
            }

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при блокировке аккаунта {email}: {e}")
            self.db_session.rollback()
            return {
                "error": f"Ошибка при блокировке аккаунта: {str(e)}",
                "success": False
            }

    def unlock_account(self, email: str) -> dict:
        """Разблокировка аккаунта - возвращает готовый ответ"""

        try:
            # Ищем пользователя
            user = self.db_session.query(User).filter(
                User.email == email
            ).first()

            if not user:
                return {
                    "error": f"Пользователь с email {email} не найден",
                    "success": False
                }

            # Разблокируем пользователя
            user.is_locked = False
            user.locked_until = None
            user.lock_reason = None
            user.updated_at = datetime.now()

            self.db_session.commit()

            return {
                "message": f"Аккаунт {email} разблокирован",
                "success": True
            }

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при разблокировке аккаунта {email}: {e}")
            self.db_session.rollback()
            return {
                "error": f"Ошибка при разблокировке аккаунта: {str(e)}",
                "success": False
            }

    def is_account_locked(self, email: str) -> Tuple[bool, Optional[str]]:
        """Проверка, заблокирован ли аккаунт"""

        try:
            user = self.db_session.query(User).filter(
                User.email == email
            ).first()

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
