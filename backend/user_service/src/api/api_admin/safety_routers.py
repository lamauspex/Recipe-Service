""" Роутеры для управления пользователями """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID


from backend.user_service.src.config import settings
from backend.database_service.connection import database
from backend.user_service.src.middleware import get_current_admin_user
from backend.user_service.src.models import User
from backend.user_service.src.services import (
    LoginAttemptsService,
    SecurityService
)

from backend.database_service.database import get_db_dependency, get_db_context, Container
from dependency_injector.wiring import Provide


router = APIRouter(
    prefix="/admins",
    tags=["Admin_Service"]
)


@router.get(
    "/security/login-logs",
    summary="Логи входов пользователей"
)
def get_login_logs(
    user_id: Optional[UUID] = None,
    ip_address: Optional[str] = None,
    days: int = 7,
    limit: int = 100,
    db: Session = Depends(get_db_dependency)
):
    """Получение логов входов пользователей"""
    user_service = LoginAttemptsService(db)
    logs = user_service.get_login_logs(
        user_id=user_id,
        ip_address=ip_address,
        days=days,
        limit=limit
    )

    return logs


@router.post(
    "/security/block-ip",
    summary="Блокировка IP адреса"
)
def block_ip_address(
    ip_address: str,
    reason: str,
    duration_hours: Optional[int] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(database.get_db)
):
    """Блокировка IP адреса"""
    user_service = SecurityService(config=settings)
    user_service.block_ip_address(
        ip_address=ip_address,
        reason=reason,
        duration_hours=duration_hours,
        admin_id=str(current_user.id)
    )

    return {"message": f"IP адрес {ip_address} заблокирован"}
