

from backend.service_user.src.exception.base import ConflictException
from backend.service_user.src.protocols.user_repository import (
    UserRepositoryProtocol)


class UserUniquenessValidator:
    """Валидатор уникальности пользователя"""

    def __init__(
        self,
        user_repo: UserRepositoryProtocol
    ):
        self.user_repo = user_repo

    def validate(
        self,
        user_name: str,
        email: str
    ) -> None:
        """ Проверка уникальности username и email """

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
