
from backend.user_service.src.config.config_auth import AuthConfig
from backend.user_service.src.protocols.user_repository import (
    UserRepositoryProtocol)
from backend.user_service.src.schemas import (
    UserCreate,
    UserResponseDTO
)
from backend.user_service.src.core.service_password import PasswordService
from backend.user_service.src.service.register_service.mappers import (
    UserRegistrationMapper)
from backend.user_service.src.core.validator_name import (
    UserUniquenessValidator)


class RegisterService:
    """ Сервис регистрации пользователя """

    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        password_service: PasswordService,
        auth_config: AuthConfig,
    ):
        self.user_repo = user_repo
        self.password_service = password_service
        self.auth_config = auth_config

        # Компоненты сервиса
        self.validator = UserUniquenessValidator(user_repo)
        self.mapper = UserRegistrationMapper(password_service)

    def register_user(self, user_data: UserCreate) -> UserResponseDTO:
        """
        Регистрация пользователя
        Returns:
            UserResponseDTO: Данные созданного пользователя
        """

        # 1. Валидация
        self.validator.validate(user_data.user_name, user_data.email)

        # 2. Маппинг (хеширование пароля)
        user_dto = self.mapper.api_to_dto(user_data)

        # 3. Создание
        user = self.user_repo.create_user_with_default_role(
            user_dto.to_repository_dict())

        # 4. Возврат DTO
        return self.mapper.model_to_response_dto(user)
