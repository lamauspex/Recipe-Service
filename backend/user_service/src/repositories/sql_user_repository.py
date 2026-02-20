from sqlalchemy.orm import Session

from backend.shared.models import User
from backend.user_service.src.exception.base import ConflictException


class SQLUserRepository:
    """
    SQLAlchemy реализация репозитория пользователей.

    ВАЖНО: Мы НЕ наследуемся от UserRepositoryProtocol!
    Protocol проверяет только наличие методов с нужными сигнатурами.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_user_with_default_role(self, user_data: dict) -> User:
        """
        Создание пользователя с ролью по умолчанию.

        Роль передаётся в словаре user_data (role_name).
        Роли теперь статические, не хранятся в БД.

        Args:
            user_data: Словарь с данными пользователя (включая role_name)

        Returns:
            User: Созданная модель пользователя

        Raises:
            ConflictException: Если роль не указана или недопустима
        """

        # Проверяем, что роль указана
        role_name = user_data.get('role_name', 'user')

        # Проверяем, что роль допустимая
        from backend.shared.models.identity.role import ROLES
        if role_name not in ROLES:
            raise ConflictException(
                f"Роль '{role_name}' не найдена. "
                f"Допустимые роли: {', '.join(ROLES.keys())}"
            )

        # Создаём пользователя
        user = User(**user_data)

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
