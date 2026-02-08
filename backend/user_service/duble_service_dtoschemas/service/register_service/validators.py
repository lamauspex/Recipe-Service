
from backend.user_service.duble_service_dtoschemas.protocols.user_repository import UserRepositoryProtocol
from backend.user_service.src.exceptions.base import ConflictException


class UserUniquenessValidator:
    """Валидатор уникальности пользователя"""

    def __init__(
        self,
        user_repo: UserRepositoryProtocol
    ):
        self.user_repo = user_repo

    def validate(self, user_name: str, email: str) -> None:
        """Проверка уникальности username и email"""

        if self.user_repo.get_user_by_user_name(user_name):
            raise ConflictException(
                message="Пользователь с таким именем уже существует",
                details={"field": "user_name", "value": user_name}
            )

        if self.user_repo.get_user_by_email(email):
            raise ConflictException(
                message="Пользователь с таким email уже существует",
                details={"field": "email", "value": email}
            )
