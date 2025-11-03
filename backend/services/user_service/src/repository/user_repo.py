"""
Repository слой для работы с пользователями
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from backend.services.user_service.models.user_models import User


class UserRepository:
    """Репозиторий для работы с пользователями"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Получение пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, user_name: str) -> Optional[User]:
        """Получение пользователя по user_name"""
        return self.db.query(User).filter(User.user_name == user_name).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user_data: dict) -> User:
        """Создание пользователя"""
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: UUID, update_data: dict) -> Optional[User]:
        """Обновление пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

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


# Для обратной совместимости
class Repository(UserRepository):
    """Репозиторий для работы с пользователями (устаревшее название)"""
    pass
