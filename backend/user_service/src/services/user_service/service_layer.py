"""
Здесь размещаются сервисные классы
или функции, которые выполняют
операции с пользователями
"""

from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from passlib.context import CryptContext

from backend.user_service.src.repository import UserRepository
from backend.user_service.src.models import User


class UserService:
    """ Сервис для работы с пользователями """

    def __init__(self, db_session):
        # Создаем репозиторий внутри сервиса (как в других сервисах!)
        self.repo = UserRepository(db_session)
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

    def request_reset_password_response(self, email: str) -> dict:
        """Запрос сброса пароля - возвращает готовый ответ"""

        try:
            user = self.get_user_by_email(email)
            if not user:
                # Не раскрываем информацию о существовании email
                return {
                    "message": "Если email зарегистрирован, вы получите письмо с инструкциями",
                    "success": True
                }

            # В реальном приложении здесь была бы отправка email
            # Пока что просто возвращаем успех
            return {
                "message": "Если email зарегистрирован, вы получите письмо с инструкциями",
                "success": True
            }

        except Exception as e:
            return {
                "error": f"Ошибка при обработке запроса: {str(e)}",
                "success": False
            }

    def confirm_password_reset_response(self, token: str, new_password: str) -> dict:
        """Подтверждение сброса пароля - возвращает готовый ответ"""

        try:
            # В реальном приложении здесь была бы проверка токена
            # Пока что просто возвращаем успех
            return {
                "message": "Пароль успешно сброшен",
                "success": True
            }

        except Exception as e:
            return {
                "error": f"Ошибка при сбросе пароля: {str(e)}",
                "success": False
            }

    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""

        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверка пароля"""

        return self.pwd_context.verify(password, hashed_password)
