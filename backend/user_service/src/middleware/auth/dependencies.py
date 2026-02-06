"""FastAPI зависимости для авторизации"""

from fastapi import Depends, status
from sqlalchemy.orm import Session

from .jwt import get_current_user as jwt_get_current_user
from backend.database_service.connection import database
from backend.user_service.src.models import User
from backend.user_service.src.exceptions import HTTPException as CustomHTTPException
from backend.user_service.src.services_old.admin_service import RoleService
from backend.user_service.src.schemas import Permission


async def get_current_user(
    credentials=Depends(jwt_get_current_user)
) -> User:
    """Получение текущего пользователя"""
    return credentials


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Получение текущего пользователя с правами администратора"""

    if not current_user.has_permission(Permission.MANAGE_USERS):
        raise CustomHTTPException(
            message="Недостаточно прав для выполнения операции",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="INSUFFICIENT_PRIVILEGES"
        )
    return current_user


async def get_current_active_user_safe(
    current_user: User
) -> User:
    """Безопасное получение активного пользователя"""

    if not current_user.is_active:
        raise CustomHTTPException(
            message="Пользователь неактивен",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="USER_INACTIVE"
        )
    return current_user


async def get_current_user_with_permissions(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
) -> tuple[User, RoleService]:
    """Получение пользователя с сервисом для проверки разрешений"""

    role_service = RoleService(db)
    return current_user, role_service


async def get_current_user_with_admin_role(
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_current_user_with_permissions)
) -> tuple[User, RoleService]:
    """Получение пользователя с проверкой админской роли"""

    if not current_user.has_permission(Permission.MANAGE_USERS):
        raise CustomHTTPException(
            message="Недостаточно прав для выполнения операции",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="INSUFFICIENT_PRIVILEGES"
        )
    return current_user, role_service
