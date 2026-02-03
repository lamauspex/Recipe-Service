""" Роутеры для админки """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from backend.database_service.connection import database
from backend.user_service.src.middleware import get_current_admin_user
from backend.user_service.src.models import User, RoleModel
from backend.user_service.src.services import UserManagementService
from backend.user_service.src.schemas import UserResponse


router = APIRouter(
    prefix="/admins",
    tags=["Admin_Service"]
)


@router.post("/bulk/action",
             summary="Массовое действие над пользователями")
def bulk_user_action(
    action: str,
    user_ids: List[UUID],
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(database.get_db)
):
    """Массовое действие над списком пользователей"""

    user_service = UserManagementService(db)
    result = user_service.bulk_user_action(
        action=action,
        user_ids=user_ids,
        reason=reason,
        admin_id=str(current_user.id)
    )

    return {
        "message": (
            f"Массовое действие '{action}' выполнено для "
            f"{len(user_ids)} пользователей"
        ),
        "details": result
    }


@router.get("/",
            response_model=None,
            summary="Получение списка пользователей")
def get_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(database.get_db)
):
    """Получение списка пользователей с фильтрацией"""

    # Конвертируем строку роли в SQLAlchemy модель если указана
    role_model = None
    if role:
        role_model = db.query(RoleModel).filter(RoleModel.name == role).first()
        if not role_model:
            raise ValueError(f"Роль '{role}' не найдена")

    user_service = UserManagementService(db)
    users = user_service.get_users_with_filters(
        skip=skip,
        limit=limit,
        search=search,
        role=role_model,
        is_active=is_active
    )

    # Конвертируем SQLAlchemy модели в Pydantic схемы
    return [UserResponse.model_validate(user) for user in users]


@router.put("/{user_id}/status",
            summary="Изменение статуса пользователя")
def change_user_status(
    user_id: UUID,
    action: str,
    reason: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """Изменение статуса пользователя (активация, блокировка и т.д.)"""

    user_service = UserManagementService(db)
    user_service.change_user_status(user_id, action, reason)

    return {"message": f"Статус пользователя изменен на: {action}"}


@router.delete("/{user_id}",
               summary="Удаление пользователя")
def delete_user(
    user_id: UUID,
    reason: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """Удаление пользователя (мягкое удаление)"""

    user_service = UserManagementService(db)
    user_service.soft_delete_user(user_id, reason)

    return {"message": "Пользователь успешно удален"}
