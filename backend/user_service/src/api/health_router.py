"""
Рутину для проверки работоспособности
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from dependency_injector.wiring import inject, Provide

from backend.user_service.src.config import settings
from backend.database_service.container import Container
from backend.user_service.src.repository import UserRepository


router_1 = APIRouter(
    prefix="/api/v1/users",
    tags=["Health_Service"]
)


@router_1.get(
    "/health",
    summary="Проверка состояния сервиса",
)
@inject
async def health_check(
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Проверка состояния сервиса и базы данных"""

    try:
        # Проверяем подключение к базе данных через сервис
        user_repo = UserRepository(db_session)
        user_repo.db.execute("SELECT 1")  # Простая проверка соединения

        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "user-service",
        "database": db_status,
        "version": settings.api.API_VERSION
    }
