
from sqlalchemy.orm import Session

from backend.user_service.src.exceptions.base import ConflictException
from backend.user_service.src.models.user_models import User
from backend.user_service.src.repository.role_repo import RoleRepository


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_user_with_default_role(self, user_data: dict) -> User:
        """Создание пользователя с ролью по умолчанию"""

        # Ищем роль внутри репозитория
        role_repo = RoleRepository(self.db)

        default_role = role_repo.get_role_by_name("user")
        if not default_role:
            raise ConflictException("Роль 'user' не найдена")

        # Создаём с ролью
        user = User(**user_data)
        user.roles.append(default_role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
