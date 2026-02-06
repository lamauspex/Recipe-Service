"""
API ручки для управления ролями
"""

from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide

from backend.user_service.src.middleware import get_current_admin_user
from backend.user_service.src.models import User
from backend.user_service.src.services_old import RoleService
from backend.database_service.container import Container
from backend.user_service.src.schemas import (
    RoleCreate,
    RoleUpdate
)


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


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой роли",
    description="Создание новой роли с набором разрешений. \
        Доступно только администраторам."
)
@inject
async def create_role(
    role_data: RoleCreate,
    _: User = Depends(get_current_admin_user),
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Создание новой роли"""

    role_service = RoleService(db_session)
    return role_service.create_role_response(role_data)


@router.get(
    "/",
    summary="Получение списка всех ролей"
)
@inject
async def list_roles(
    _: User = Depends(get_current_admin_user),
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Получение списка ролей"""

    role_service = RoleService(db_session)
    return role_service.get_all_roles_response()


@router.get(
    "/{role_id}",
    summary="Получение информации о роли"
)
@inject
async def get_role(
    role_id: UUID,
    _: User = Depends(get_current_admin_user),
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Получение роли по ID"""

    role_service = RoleService(db_session)
    return role_service.get_role_by_id_response(str(role_id))


@router.put(
    "/{role_id}",
    summary="Обновление роли"
)
@inject
async def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    _: User = Depends(get_current_admin_user),
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Обновление роли"""

    role_service = RoleService(db_session)
    return role_service.update_role_response(str(role_id), role_data)


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление роли"
)
@inject
async def delete_role(
    role_id: UUID,
    _: User = Depends(get_current_admin_user),
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Удаление роли (мягкое)"""

    role_service = RoleService(db_session)
    return role_service.delete_role_response(str(role_id))
