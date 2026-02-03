"""
API ручки для управления ролями
"""

from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from backend.database_service import database
from backend.user_service.src.middleware import get_current_admin_user
from backend.user_service.src.models import User
from backend.user_service.src.services import RoleService
from backend.user_service.src.schemas import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
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
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой роли",
    description="Создание новой роли с набором разрешений. \
        Доступно только администраторам."
)
async def create_role(
    role_data: RoleCreate,
    _: User = Depends(get_current_admin_user),
    db: Session = Depends(database.get_db)
):
    """Создание новой роли"""
    role_service = RoleService(db)

    role = role_service.create_role(
        name=role_data.name,
        display_name=role_data.display_name,
        permissions=role_data.permissions,
        description=role_data.description
    )

    return RoleResponse.from_orm(role)


@router.get(
    "/",
    response_model=List[RoleResponse],
    summary="Получение списка всех ролей"
)
async def list_roles(
    _: User = Depends(get_current_admin_user),
    db: Session = Depends(database.get_db)
):
    """Получение списка ролей"""
    role_service = RoleService(db)
    roles = role_service.get_all_roles()
    return [RoleResponse.from_orm(r) for r in roles]


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Получение информации о роли"
)
async def get_role(
    role_id: UUID,
    _: User = Depends(get_current_admin_user),
    db: Session = Depends(database.get_db)
):
    """Получение роли по ID"""

    role_service = RoleService(db)
    role = role_service.get_role_by_id(str(role_id))

    return RoleResponse.from_orm(role)


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Обновление роли"
)
async def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    _: User = Depends(get_current_admin_user),
    db: Session = Depends(database.get_db)
):
    """Обновление роли"""

    role_service = RoleService(db)
    role = role_service.update_role(
        str(role_id),
        role_data.model_dump(exclude_unset=True)
    )

    return RoleResponse.from_orm(role)


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление роли"
)
async def delete_role(
    role_id: UUID,
    _: User = Depends(get_current_admin_user),
    db: Session = Depends(database.get_db)
):
    """Удаление роли (мягкое)"""

    role_service = RoleService(db)
    role_service.delete_role(str(role_id))
