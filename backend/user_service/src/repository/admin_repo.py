"""
Repository слой для работы с admin
"""

from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from user_service.models import User


class AdminRepository:

    def __init__(self, db: Session):
        self.db = db

    def delete_user(self, user_id: UUID) -> bool:
        """Удаление пользователя"""

        user = self.get_user_by_id(user_id)

        if not user:
            return False

        self.db.delete(user)
        self.db.commit()

        return True

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей"""

        return self.db.query(User).offset(skip).limit(limit).all()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка активных пользователей"""

        return self.db.query(User).filter(
            User.is_active.is_(True)
        ).offset(skip).limit(limit).all()
