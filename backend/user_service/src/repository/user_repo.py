"""
Repository слой для работы с пользователями
"""

from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from backend.user_service.src.models import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Получение пользователя по ID"""

        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_user_name(self, user_name: str) -> Optional[User]:
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
