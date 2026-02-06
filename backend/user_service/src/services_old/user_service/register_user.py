"""
Сервис для регистрации пользователей
Обновлен для использования базового класса и утилиты паролей
"""

from datetime import datetime, timezone

from backend.user_service.src.exceptions.base import ConflictException
from backend.user_service.src.models.role_model import RoleModel
from backend.user_service.src.repository import UserRepository
from backend.user_service.src.schemas import UserCreate
from common.base_service import BaseService
from common.response_builder import ResponseBuilder
from common.password_utility import password_utility


class RegisterService(BaseService):
    """Сервис для регистрации пользователей"""

    def __init__(self, db_session):
        super().__init__()
        self.repo = UserRepository(db_session)

    def register_user(self, user_data: UserCreate) -> dict:
        """Регистрация нового пользователя"""
        try:
            # Проверка существования пользователя
            existing_user = self.repo.get_user_by_user_name(
                user_data.user_name)
            if existing_user:
                return ResponseBuilder.error(
                    "Пользователь с таким именем уже существует",
                    error_code="USERNAME_EXISTS",
                    details={"field": "user_name",
                             "value": user_data.user_name}
                )

            existing_email = self.repo.get_user_by_email(user_data.email)
            if existing_email:
                return ResponseBuilder.error(
                    "Пользователь с таким email уже существует",
                    error_code="EMAIL_EXISTS",
                    details={"field": "email", "value": user_data.email}
                )

            # Хеширование пароля с использованием утилиты
            hashed_password = password_utility.hash_password(
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

            # Добавление роли
            session = self.repo.db
            initial_role = session.query(RoleModel).filter(
                RoleModel.name == "user").first()
            if initial_role:
                user.add_role(initial_role)

            return ResponseBuilder.success(
                "Пользователь успешно зарегистрирован",
                data={
                    "id": str(user.id),
                    "user_name": user.user_name,
                    "email": user.email,
                    "full_name": user.full_name
                }
            )

        except ConflictException as e:
            return ResponseBuilder.error(
                str(e),
                error_code="CONFLICT",
                details=e.details
            )
        except Exception as e:
            return self._handle_error(e, "регистрации пользователя")
