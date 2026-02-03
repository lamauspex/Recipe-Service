"""
Сервис для регистрации пользователей
"""

from datetime import datetime, timezone

from user_service.exceptions.base import ConflictException
from user_service.models.role_model import RoleModel
from user_service.repository import UserRepository
from user_service.schemas import UserCreate
from user_service.models import User
from user_service.services.auth_service import PasswordService


class RegisterService:

    def __init__(
            self,
            repo: UserRepository,
            password_service: PasswordService = None
    ):
        """
        : param repo: Репозиторий для работы с пользователями
        : param password_service: Сервис для работы с паролями
        : return: None
        """

        self.repo = repo
        self.password_service = password_service or PasswordService()

    def register_user(self, user_data: UserCreate) -> User:
        """Регистрация нового пользователя"""

        existing_user = self.repo.get_user_by_user_name(user_data.user_name)
        if existing_user:
            raise ConflictException(
                message="Пользователь с таким именем уже существует",
                details={"field": "user_name", "value": user_data.user_name}
            )

        existing_email = self.repo.get_user_by_email(user_data.email)
        if existing_email:
            raise ConflictException(
                message="Пользователь с таким email уже существует",
                details={"field": "email", "value": user_data.email}
            )

        # Используем централизованный сервис для хеширования
        hashed_password = self.password_service.hash_password(
            user_data.password)

        # Создание пользователя
        user_dict = {
            "user_name": user_data.user_name,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "email_verified": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        user = self.repo.create_user(user_dict)

        # После создания добавляем роль
        session = self.repo.db
        initial_role = session.query(RoleModel).filter(
            RoleModel.name == "user").first()
        if initial_role:
            user.add_role(initial_role)

        return user
