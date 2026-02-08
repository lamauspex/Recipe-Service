""" Роутеры для админки """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from dependency_injector.wiring import inject, Provide

from backend.user_service.src.middleware import get_current_admin_user
from backend.user_service.src.models import User
from backend.user_service.src.services import UserManagementService
from backend.database_service.container import Container


router = APIRouter(
    prefix="/admins",
    tags=["Admin_Service"]
)


@router.post(
    "/bulk/action",
    summary="Массовое действие над пользователями"
)
@inject
def bulk_user_action(
    action: str,
    user_ids: List[UUID],
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Массовое действие над списком пользователей"""

    user_service = UserManagementService(db_session)
    return user_service.bulk_user_action(
        action=action,
        user_ids=user_ids,
        reason=reason,
        admin_id=str(current_user.id)
    )


@router.get(
    "/",
    response_model=None,
    summary="Получение списка пользователей"
)
@inject
def get_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Получение списка пользователей с фильтрацией"""

    user_service = UserManagementService(db_session)
    return user_service.get_users_with_filters_response(
        skip=skip,
        limit=limit,
        search=search,
        role=role,
        is_active=is_active
    )


@router.put(
    "/{user_id}/status",
    summary="Изменение статуса пользователя"
)
@inject
def change_user_status(
    user_id: UUID,
    action: str,
    reason: Optional[str] = None,
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Изменение статуса пользователя (активация, блокировка и т.д.)"""

    user_service = UserManagementService(db_session)
    return user_service.change_user_status(user_id, action, reason)


@router.delete(
    "/{user_id}",
    summary="Удаление пользователя"
)
@inject
def delete_user(
    user_id: UUID,
    reason: Optional[str] = None,
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Удаление пользователя (мягкое удаление)"""

    user_service = UserManagementService(db_session)
    return user_service.soft_delete_user(user_id, reason)
