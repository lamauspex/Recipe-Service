from sqlalchemy.orm import Session

from backend.user_service.duble_service_dtoschemas.protocols import (
    UserRepositoryProtocol,
    RoleRepositoryProtocol
)
from backend.user_service.duble_service_dtoschemas.repositories import (
    SQLUserRepository,
    SQLRoleRepository
)


class RepositoryFactory:
    """
    Фабрика для создания репозиториев.

    В будущем можно добавить методы для других реализаций:
    - create_mongo_user_repository()
    - create_file_user_repository()
    и т.д.
    """

    @staticmethod
    def create_user_repository(
        db: Session
    ) -> UserRepositoryProtocol:
        """
        Создаёт SQL репозиторий пользователей

        :param db: Сессия базы данных
        :return: Репозиторий пользователей
        """
        return SQLUserRepository(db)

    @staticmethod
    def create_role_repository(
        db: Session
    ) -> RoleRepositoryProtocol:
        """
        Создаёт SQL репозиторий ролей

        :param db: Сессия базы данных
        :return: Репозиторий ролей
        """
        return SQLRoleRepository(db)

    @staticmethod
    def create_all_repositories(
        db: Session
    ) -> tuple[UserRepositoryProtocol, RoleRepositoryProtocol]:
        """
        Создаёт все репозитории за один вызов

        :param db: Сессия базы данных
        :return: Кортеж (user_repo, role_repo)
        """
        user_repo = RepositoryFactory.create_user_repository(db)
        role_repo = RepositoryFactory.create_role_repository(db)
        return user_repo, role_repo
