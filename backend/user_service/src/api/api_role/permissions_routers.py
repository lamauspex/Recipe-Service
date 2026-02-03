"""
API ручки для управления ролями
"""


from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.database_service import database
from backend.user_service.src.middleware import get_current_admin_user
from backend.user_service.src.models import User, Permission
from backend.user_service.src.services import RoleService
from backend.user_service.src.services.admin_service import role_service

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
    response_model=List[str],
    summary="Получение списка доступных разрешений"
)
async def get_available_permissions(
    _: User = Depends(get_current_admin_user)
):
    """Получение списка доступных разрешений"""

    return sorted([p.name for p in Permission if p != Permission.NONE])


@router.get(
    "/user-permissions/{user_id}",
    response_model=List[str],
    summary="Получение всех разрешений пользователя"
)
async def get_user_permissions(
    user_id: UUID,
    _: User = Depends(get_current_admin_user),
    db: Session = Depends(database.get_db)
):
    """Получение всех разрешений пользователя"""

    user = db.query(User).filter(User.id == user_id).first()

    role_service = RoleService(db)
    perms = role_service.get_user_permissions(user)

    return [p.name for p in perms]


@router.get(
    "/user-permissions/check/{user_id}/{permission}",
    response_model=dict,
    summary="Проверка наличия разрешения у пользователя"
)
async def check_user_permission(
    user_id: UUID,
    permission: str,
    _: User = Depends(get_current_admin_user),
    db: Session = Depends(database.get_db)
):
    """Проверка наличия разрешения у пользователя"""

    user = db.query(User).filter(User.id == user_id).first()

    perm = Permission[permission.upper()]
    has_perm = role_service.user_has_permission(user, perm)

    return {
        "user_id": str(user_id),
        "permission": permission,
        "has_permission": has_perm
    }
