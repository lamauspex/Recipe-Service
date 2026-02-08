"""
Сервис для регистрации пользователей
"""


from sqlalchemy.orm import Session

from backend.user_service.src.repository.role_repo import RoleRepository
from backend.user_service.src.schemas.auth_schemas.register_schemas import UserRegistrationDTO
from user_service.src.exceptions.base import ConflictException
from user_service.src.repository import UserRepository
from user_service.src.schemas import UserCreate
from user_service.src.models import User
from user_service.src.services.auth_service import PasswordService


class RegisterService:

    def __init__(
            self,
            db_session: Session,
            repo: UserRepository,
            password_service: PasswordService | None = None,
            role_repo: RoleRepository | None = None
    ):

        self.db = db_session
        # Создаём репозитории внутри сервиса на основе сессии
        self.user_repo = UserRepository(db_session)
        self.role_repo = role_repo or RoleRepository(db_session)
        self.password_service = password_service or PasswordService()

    def register_user(self, user_data: UserCreate) -> User:
        """Регистрация нового пользователя"""

        # 1. Проверка уникальности
        self._validate_user_uniqueness(user_data)

        # 2. Подготовка данных (хеширование пароля)
        user_dto = self._prepare_registration_dto(user_data)

        # 3. Создание пользователя через репозиторий
        user = self.user_repo.create_user(user_dto.to_dict())

        # 4. Назначение базовой роли
        self._assign_default_role(user)

        return user

    def register_user_from_dto(self, user_dto: UserRegistrationDTO) -> User:
        """Регистрация пользователя из DTO (для внутреннего использования)"""

        if self.repo.get_user_by_user_name(user_dto.user_name):

            raise ConflictException(
                message="Пользователь с таким именем уже существует",
                details={"field": "user_name", "value": user_dto.user_name}
            )

        if self.repo.get_user_by_email(user_dto.email):
            raise ConflictException(
                message="Пользователь с таким email уже существует",
                details={"field": "email", "value": user_dto.email}
            )
        # Создание пользователя
        user = self.user_repo.create_user(user_dto.to_dict())

        # Назначение базовой роли
        self._assign_default_role(user)

        return user

    def _validate_user_uniqueness(self, user_data: UserCreate) -> None:
        """Проверка уникальности пользователя"""

        if self.user_repo.get_user_by_user_name(user_data.user_name):
            raise ConflictException(
                message="Пользователь с таким именем уже существует",
                details={"field": "user_name", "value": user_data.user_name}
            )

        if self.user_repo.get_user_by_email(user_data.email):
            raise ConflictException(
                message="Пользователь с таким email уже существует",
                details={"field": "email", "value": user_data.email}
            )

    def _prepare_registration_dto(
        self,
        user_data: UserCreate
    ) -> UserRegistrationDTO:
        """ Подготовка DTO из API схемы """

        hashed_password = self.password_service.hash_password(
            user_data.password)

        return UserRegistrationDTO(
            user_name=user_data.user_name,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            email_verified=False
        )

    def _assign_default_role(self, user: User) -> None:
        """Назначение базовой роли пользователю"""

        default_role = self.role_repo.get_role_by_name("user")
        if default_role:
            user.add_role(default_role)
