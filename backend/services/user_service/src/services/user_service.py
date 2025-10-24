"""
Сервис для работы с пользователями
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from backend.services.user_service.src.models import User
from backend.services.user_service.src.schemas import UserCreate, UserUpdate


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        """Создание нового пользователя"""
        from .auth_service import AuthService

        auth_service = AuthService(self.db)
        hashed_password = auth_service.get_password_hash(user_data.password)

        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            bio=user_data.bio
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def get_user(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def update_user(self,
                    user_id: int,
                    user_data: UserUpdate
                    ) -> Optional[User]:
        """Обновление данных пользователя"""
        user = self.get_user(user_id)
        if not user:
            return None

        update_data = user_data.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)

        return user

    def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя"""
        user = self.get_user(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()

        return True

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def activate_user(self, user_id: int) -> Optional[User]:
        """Активация пользователя"""
        user = self.get_user(user_id)
        if not user:
            return None

        user.is_active = True
        self.db.commit()
        self.db.refresh(user)

        return user

    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Деактивация пользователя"""
        user = self.get_user(user_id)
        if not user:
            return None

        user.is_active = False
        self.db.commit()
        self.db.refresh(user)

        return user

    def set_admin(self, user_id: int, is_admin: bool = True) -> Optional[User]:
        """Установка прав администратора"""
        user = self.get_user(user_id)
        if not user:
            return None

        user.is_admin = is_admin
        self.db.commit()
        self.db.refresh(user)

        return user
