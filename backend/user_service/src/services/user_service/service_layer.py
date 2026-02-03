
"""
Здесь размещаются сервисные классы
или функции, которые выполняют
операции с пользователями
"""

from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from passlib.context import CryptContext

from user_service.repository import UserRepository
from user_service.models import User


class UserService:
    """ Сервис для работы с пользователями """

    def __init__(self, repo: UserRepository):
        self.repo = repo
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto"
        )

    def update_user(self, user_id: UUID, user_data) -> Optional[User]:
        """Обновление данных пользователя"""

        if isinstance(user_data, dict):
            update_data = user_data
        elif hasattr(user_data, 'model_dump'):
            update_data = user_data.model_dump(exclude_unset=True)
        else:
            update_data = user_data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)
        return self.repo.update_user(user_id, update_data)

    def get_user(self, user_id: UUID) -> Optional[User]:
        """Получение пользователя по ID"""

        return self.repo.get_user_by_id(user_id)

    def get_user_by_user_name(self, user_name: str) -> Optional[User]:
        """Получение пользователя по имени"""

        return self.repo.get_user_by_user_name(user_name)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""

        return self.repo.get_user_by_email(email)
