from sqlalchemy.orm import Session

from backend.user_service.duble_service_dtoschemas.protocols import (
    UserRepositoryProtocol,
    RoleRepositoryProtocol
)
from backend.user_service.duble_service_dtoschemas.protocols.token_repository import TokenRepositoryProtocol
from backend.user_service.duble_service_dtoschemas.repositories import (
    SQLUserRepository,
    SQLRoleRepository
)
from backend.user_service.duble_service_dtoschemas.repositories.sql_token_repository import SQLTokenRepository


class RepositoryFactory:
    """ Фабрика для создания репозиториев """

    @staticmethod
    def create_user_repository(
        db: Session
    ) -> UserRepositoryProtocol:
        """ Создаёт SQL репозиторий пользователей """
        return SQLUserRepository(db)

    @staticmethod
    def create_role_repository(
        db: Session
    ) -> RoleRepositoryProtocol:
        """ Создаёт SQL репозиторий ролей """
        return SQLRoleRepository(db)

    @staticmethod
    def create_token_repository(db: Session) -> TokenRepositoryProtocol:
        """ Создаёт SQL репозиторий для аутентификации """
        return SQLTokenRepository(db)

    @staticmethod
    def create_all_repositories(
        db: Session
    ) -> tuple[
        UserRepositoryProtocol,
        RoleRepositoryProtocol,
        TokenRepositoryProtocol
    ]:
        """ Создаёт все репозитории за один вызов """

        user_repo = RepositoryFactory.create_user_repository(db)
        role_repo = RepositoryFactory.create_role_repository(db)
        token_repo = RepositoryFactory.create_token_repository(db)

        return user_repo, role_repo, token_repo
