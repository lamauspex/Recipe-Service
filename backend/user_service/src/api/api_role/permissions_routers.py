""" API ручки для управления разрешениями """

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide

from backend.database_service.container import Container
from backend.user_service.src.middleware import get_current_admin_user
from backend.user_service.src.models import User
from backend.user_service.src.services_old import RoleService

router = APIRouter(
    prefix="/roles",
    tags=["Roles Management"],
    responses={
        401: {"description": "Неавторизован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Роль не найдена"},
        500: {"description": "Внутренняя ошибка сервера"}
    }
)


@router.get(
    "/available-permissions",
    summary="Получение списка доступных разрешений"
)
@inject
async def get_available_permissions(
    _: User = Depends(get_current_admin_user),
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Получение списка доступных разрешений"""

    role_service = RoleService(db_session)
    return role_service.get_available_permissions_response()


@router.get(
    "/user-permissions/{user_id}",
    summary="Получение всех разрешений пользователя"
)
@inject
async def get_user_permissions(
    user_id: UUID,
    _: User = Depends(get_current_admin_user),
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Получение всех разрешений пользователя"""

    role_service = RoleService(db_session)
    return role_service.get_user_permissions_response(str(user_id))


@router.get(
    "/user-permissions/check/{user_id}/{permission}",
    summary="Проверка наличия разрешения у пользователя"
)
@inject
async def check_user_permission(
    user_id: UUID,
    permission: str,
    _: User = Depends(get_current_admin_user),
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Проверка наличия разрешения у пользователя"""

    role_service = RoleService(db_session)
    return role_service.check_user_permission_response(
        str(user_id),
        permission
    )
