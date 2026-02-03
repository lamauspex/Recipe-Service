
""" Рутеры для статистики """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from backend.database_service import database
from user_service.services import StatisticsService


router = APIRouter(
    prefix="/admins",
    tags=["Admin_Service"]
)


@router.get("/stats/overview",
            summary="Общая статистика")
def get_stats_overview(
    db: Session = Depends(database.get_db)
):
    """Получение общей статистики пользователей"""
    user_service = StatisticsService(db)
    stats = user_service.get_admin_stats()

    return stats


@router.get("/stats/recent-registrations",
            summary="Недавние регистрации")
def get_recent_registrations(
    days: int = 7,
    db: Session = Depends(database.get_db)
):
    """Получение списка недавних регистраций"""
    user_service = StatisticsService(db)
    registrations = user_service.get_recent_registrations(days=days)

    return registrations


@router.get("/stats/login-attempts",
            summary="Статистика попыток входа")
def get_login_attempts_stats(
    days: int = 7,
    db: Session = Depends(database.get_db)
):
    """Получение статистики попыток входа"""
    user_service = StatisticsService(db)
    stats = user_service.get_login_attempts_stats(days=days)

    return stats
