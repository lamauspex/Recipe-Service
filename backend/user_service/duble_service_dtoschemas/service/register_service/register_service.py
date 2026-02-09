
from backend.user_service.duble_service_dtoschemas.protocols.user_repository import UserRepositoryProtocol
from backend.user_service.duble_service_dtoschemas.schemas import (
    UserCreate,
    UserResponseDTO
)
from backend.user_service.duble_service_dtoschemas.core.password_service import PasswordService
from backend.user_service.duble_service_dtoschemas.service.register_service.mappers import UserRegistrationMapper
from backend.user_service.duble_service_dtoschemas.core.validators import UserUniquenessValidator


class RegisterService:
    """ Сервис регистрации пользователя """

    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        password_service: PasswordService | None = None
    ):
        self.user_repo = user_repo

        # Компоненты сервиса
        self.validator = UserUniquenessValidator(user_repo)
        self.mapper = UserRegistrationMapper(
            password_service or PasswordService()
        )

    def register_user(self, user_data: UserCreate) -> UserResponseDTO:
        """ Регистрация пользователя """

        # 1. Валидация
        self.validator.validate(user_data.user_name, user_data.email)

        # 2. Маппинг (хеширование пароля)
        user_dto = self.mapper.api_to_dto(user_data)

        # 3. Создание
        user = self.user_repo.create_user_with_default_role(user_dto.to_dict())

        # 4. Возврат DTO
        return self.mapper.model_to_response_dto(user)
