"""
Рутину для проверки работоспособности
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.user_service.src.config import settings
from backend.database_service import database
from backend.user_service.src.repository import UserRepository


router_1 = APIRouter(
    prefix="/api/v1/users",
    tags=["Health_Service"]
)


@router_1.get("/health",
              summary="Проверка состояния сервиса",
              )
async def health_check(db: Session = Depends(database.get_db)):
    """Проверка состояния сервиса и базы данных"""

    try:
        # Проверяем подключение к базе данных через сервис
        # Пробуем выполнить простой запрос через репозиторий
        user_repo = UserRepository(db)
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
