

from backend.user_service.src.schemas import (
    UserRegistrationDTO,
    UserCreate,
    UserResponseDTO
)
from backend.user_service.src.core.service_password import PasswordService
from backend.shared.models.identity.user import User


class UserRegistrationMapper:
    """Маппер для конвертации схем"""

    def __init__(self, password_service: PasswordService):
        self.password_service = password_service

    def api_to_dto(self, user_create: UserCreate) -> UserRegistrationDTO:
        """Конвертация API схемы во внутренний DTO"""

        hashed_password = self.password_service.hash_password(
            user_create.password)

        return UserRegistrationDTO(
            user_name=user_create.user_name,
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
            is_active=True,
            email_verified=False
        )

    @staticmethod
    def model_to_response_dto(user: User) -> UserResponseDTO:
        """Конвертация модели в DTO ответа"""

        return UserResponseDTO(
            id=str(user.id),
            user_name=user.user_name,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            email_verified=user.email_verified,
            roles=[role.name for role in user.roles],
            created_at=user.created_at,
            updated_at=user.updated_at
        )
