
""" Рутеры для статистики """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide

from backend.user_service.src.services import StatisticsService
from backend.database_service.container import Container


router = APIRouter(
    prefix="/admins",
    tags=["Admin_Service"]
)


@router.get(
    "/stats/overview",
    summary="Общая статистика"
)
@inject
def get_stats_overview(
    db: Session = Depends(Provide[Container.db_dependency])
):
    """Получение общей статистики пользователей"""

    user_service = StatisticsService(db)
    stats = user_service.get_admin_stats()

    return stats


@router.get(
    "/stats/recent-registrations",
    summary="Недавние регистрации"
)
@inject
def get_recent_registrations(
    days: int = 7,
    db: Session = Depends(Provide[Container.db_dependency])
):
    """Получение списка недавних регистраций"""

    user_service = StatisticsService(db)
    registrations = user_service.get_recent_registrations(days=days)

    return registrations


@router.get(
    "/stats/login-attempts",
    summary="Статистика попыток входа"
)
@inject
def get_login_attempts_stats(
    days: int = 7,
    db: Session = Depends(Provide[Container.db_dependency])
):
    """Получение статистики попыток входа"""

    user_service = StatisticsService(db)
    stats = user_service.get_login_attempts_stats(days=days)

    return stats
