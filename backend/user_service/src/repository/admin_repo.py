"""
Repository слой для работы с admin
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from backend.user_service.src.models import User


class AdminRepository:

    def __init__(self, db: Session):
        self.db = db

    def delete_user(self, user_id: UUID, update_data: Dict[str, Any]) -> bool:
        """Мягкое удаление пользователя с обновлением данных"""

        user = self.get_user_by_id(user_id)

        if not user:
            return False

        # Обновляем поля пользователя
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.db.commit()
        return True

    def update_user(self, user_id: UUID, update_data: Dict[str, Any]) -> Optional[User]:
        """Обновление пользователя и возврат обновленного объекта"""

        user = self.get_user_by_id(user_id)

        if not user:
            return None

        # Обновляем поля пользователя
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.db.commit()
        return user

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Получение пользователя по ID"""

        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей"""

        return self.db.query(User).offset(skip).limit(limit).all()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка активных пользователей"""

        return self.db.query(User).filter(
            User.is_active.is_(True)
        ).offset(skip).limit(limit).all()
