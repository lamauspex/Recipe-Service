from sqlalchemy.orm import Session

from backend.user_service.duble_service_dtoschemas.schemas import (
    UserCreate,
    UserResponseDTO
)
from backend.user_service.duble_service_dtoschemas.service.register_service.mappers import UserRegistrationMapper
from backend.user_service.duble_service_dtoschemas.service.register_service.validators import UserUniquenessValidator
from backend.user_service.duble_service_dtoschemas.repository.register_repo import UserRepository
from backend.user_service.src.services.auth_service.password_service import PasswordService


class RegisterService:
    """ Сервис регистрации пользователя """

    def __init__(
        self,
        db_session: Session,
        password_service: PasswordService | None = None
    ):
        self.db = db_session
        self.user_repo = UserRepository(db_session)

        # Компоненты сервиса
        self.validator = UserUniquenessValidator(self.user_repo)
        self.mapper = UserRegistrationMapper(
            password_service or PasswordService()
        )

    def register_user(self, user_data: UserCreate) -> UserResponseDTO:
        """ Регистрация пользователя """

        # 1. Валидация
        self.validator.validate(user_data.user_name, user_data.email)

        # 2. Маппинг (хеширование пароля)
        user_dto = self.mapper.api_to_dto(user_data)

        # 3. Создание пользователя с ролью — один вызов!
        user = self.user_repo.create_user_with_default_role(user_dto.to_dict())

        # 4. Возврат DTO
        return self.mapper.model_to_response_dto(user)
