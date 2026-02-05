"""
Сервис для регистрации пользователей
"""

from datetime import datetime, timezone

from backend.user_service.src.exceptions.base import ConflictException
from backend.user_service.src.models.role_model import RoleModel
from backend.user_service.src.repository import UserRepository
from backend.user_service.src.schemas import UserCreate
from backend.user_service.src.services.auth_service import PasswordService


class RegisterService:

    def __init__(
            self,
            db_session,
            password_service: PasswordService = None
    ):
        """
        :param db_session: Сессия базы данных
        :param password_service: Сервис для работы с паролями
        :return: None
        """

        self.repo = UserRepository(db_session)
        self.password_service = password_service or PasswordService()

    def register_user(self, user_data: UserCreate) -> dict:
        """Регистрация нового пользователя - возвращает готовый ответ"""

        try:
            # Проверка существования пользователя
            existing_user = self.repo.get_user_by_user_name(
                user_data.user_name)
            if existing_user:
                raise ConflictException(
                    message="Пользователь с таким именем уже существует",
                    details={"field": "user_name",
                             "value": user_data.user_name}
                )

            existing_email = self.repo.get_user_by_email(user_data.email)
            if existing_email:
                raise ConflictException(
                    message="Пользователь с таким email уже существует",
                    details={"field": "email", "value": user_data.email}
                )

            # Хеширование пароля
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

            # Добавление роли
            session = self.repo.db
            initial_role = session.query(RoleModel).filter(
                RoleModel.name == "user").first()
            if initial_role:
                user.add_role(initial_role)

            return {
                "message": "Пользователь успешно зарегистрирован",
                "user": {
                    "id": str(user.id),
                    "user_name": user.user_name,
                    "email": user.email,
                    "full_name": user.full_name
                },
                "success": True
            }

        except ConflictException:
            # Перебрасываем ConflictException дальше для правильной обработки
            raise
        except Exception as e:
            return {
                "error": f"Ошибка при регистрации пользователя: {str(e)}",
                "success": False
            }
