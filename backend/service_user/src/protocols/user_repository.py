
from typing import Protocol, Optional

from backend.shared.models.identity.user import User


class UserRepositoryProtocol(Protocol):
    """
    Protocol (интерфейс) для репозитория пользователей.

    Любой класс, реализующий эти методы, может быть использован
    как UserRepositoryProtocol. Не нужно наследоваться!
    """

    def create_user_with_default_role(self, user_data: dict) -> User:
        """
        Создание пользователя с ролью по умолчанию

        :param user_data: Словарь с данными пользователя
        :return: Созданный пользователь
        """
        ...

    def get_user_by_user_name(self, user_name: str) -> Optional[User]:
        """
        Поиск пользователя по имени

        :param user_name: Имя пользователя
        :return: Пользователь или None
        """
        ...

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Поиск пользователя по email

        :param email: Email пользователя
        :return: Пользователь или None
        """
        ...

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Поиск пользователя по ID

        :param user_id: ID пользователя
        :return: Пользователь или None
        """
        ...

    def get_active_user_by_user_name(self, user_name: str) -> Optional[User]:
        """
        Поиск активного пользователя по имени

        :param user_name: Имя пользователя
        :return: Активный пользователь или None
        """
        ...
