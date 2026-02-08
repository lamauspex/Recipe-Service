""" Роутеры для управления пользователями """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from dependency_injector.wiring import inject, Provide

from backend.user_service.src.config import settings
from backend.user_service.src.middleware import get_current_admin_user
from backend.user_service.src.models import User
from backend.user_service.src.services import (
    LoginAttemptsService,
    SecurityService,
    AccountLocker,
    RateLimiter,
    SuspiciousDetector
)
from backend.database_service.container import Container
from backend.database_service.database import DataBaseConfig


router = APIRouter(
    prefix="/admins",
    tags=["Admin_Service"]
)


@router.get(
    "/security/login-logs",
    summary="Логи входов пользователей"
)
@inject
def get_login_logs(
    user_id: Optional[UUID] = None,
    ip_address: Optional[str] = None,
    days: int = 7,
    limit: int = 100,
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Получение логов входов пользователей"""

    user_service = LoginAttemptsService(db_session)
    return user_service.get_login_logs_response(
        user_id=user_id,
        ip_address=ip_address,
        days=days,
        limit=limit
    )


@router.post(
    "/security/block-ip",
    summary="Блокировка IP адреса"
)
@inject
def block_ip_address(
    ip_address: str,
    reason: str,
    duration_hours: Optional[int] = None,
    current_user: User = Depends(get_current_admin_user),
    db_session: Session = Depends(Provide[Container.db_dependency]),
    database_config: DataBaseConfig = Depends(
        Provide[Container.database_config])
):
    """Блокировка IP адреса"""

    security_service = SecurityService(db_session, database_config)
    return security_service.block_ip_address(
        ip_address=ip_address,
        reason=reason,
        duration_hours=duration_hours,
        admin_id=str(current_user.id)
    )


@router.post(
    "/security/unlock-account",
    summary="Разблокировка аккаунта"
)
@inject
def unlock_user_account(
    email: str,
    current_user: User = Depends(get_current_admin_user),
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Разблокировка пользовательского аккаунта"""

    account_locker = AccountLocker(settings, db_session)
    return account_locker.unlock_account(email)


@router.get(
    "/security/rate-limits",
    summary="Проверка лимитов запросов"
)
@inject
def get_rate_limits(
    email: Optional[str] = None,
    ip_address: Optional[str] = None,
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Получение информации о лимитах запросов"""

    rate_limiter = RateLimiter(settings, db_session)
    return rate_limiter.get_limit_info(
        email=email,
        ip_address=ip_address
    )


@router.post(
    "/security/check-suspicious",
    summary="Проверка подозрительной активности"
)
@inject
def check_suspicious_activity(
    email: str,
    user_agent: str,
    current_user: User = Depends(get_current_admin_user),
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Проверка подозрительной активности пользователя"""

    suspicious_detector = SuspiciousDetector(settings, db_session)
    return suspicious_detector.get_suspicious_activity_response(
        email,
        user_agent
    )
