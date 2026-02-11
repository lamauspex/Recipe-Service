from sqlalchemy.orm import Session

from backend.shared.models.user_models import User
from backend.user_service.src.exception.base import ConflictException
from backend.user_service.src.repositories.sql_role_repository import (
    SQLRoleRepository)


class SQLUserRepository:
    """
    SQLAlchemy реализация репозитория пользователей.

    ВАЖНО: Мы НЕ наследуемся от UserRepositoryProtocol!
    Protocol проверяет только наличие методов с нужными сигнатурами.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_user_with_default_role(self, user_data: dict) -> User:
        """Создание пользователя с ролью по умолчанию"""

        # Используем существующий RoleRepository
        role_repo = SQLRoleRepository(self.db)
        default_role = role_repo.get_role_by_name("user")

        if not default_role:
            raise ConflictException("Роль 'user' не найдена")

        # Создаём пользователя
        user = User(**user_data)
        user.roles.append(default_role)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_user_name(self, user_name: str):
        """Поиск пользователя по имени"""
        return self.db.query(User).filter(User.user_name == user_name).first()

    def get_user_by_email(self, email: str):
        """Поиск пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int):
        """Поиск пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_active_user_by_user_name(self, user_name: str):
        """Поиск активного пользователя по имени"""
        return self.db.query(User).filter(
            User.user_name == user_name,
            User.is_active is True
        ).first()
