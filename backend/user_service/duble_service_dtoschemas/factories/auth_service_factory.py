from sqlalchemy.orm import Session

from backend.user_service.duble_service_dtoschemas.core.service_jwt import JWTService
from backend.user_service.duble_service_dtoschemas.core.service_password import PasswordService
from backend.user_service.duble_service_dtoschemas.factories import RepositoryFactory
from backend.user_service.duble_service_dtoschemas.service.auth_service.auth_service import AuthService


class AuthServiceFactory:
    """Фабрика для создания AuthService"""

    @staticmethod
    def create(db_session: Session) -> AuthService:
        user_repo = RepositoryFactory.create_user_repository(db_session)
        password_service = PasswordService()
        jwt_service = JWTService()

        return AuthService(
            user_repo=user_repo,
            password_service=password_service,
            jwt_service=jwt_service
        )
