"""
API router module
"""
from fastapi import APIRouter

# Импортируем все роутеры
from .auth_user import router as auth_router
from .register_user import router as register_router
from .health import router as health_router

# Создаем главный API router
api_router = APIRouter(prefix="/api/v1")

# Подключаем все роутеры с префиксами
api_router.include_router(auth_router)
api_router.include_router(register_router)
api_router.include_router(health_router)


__all__ = ["api_router"]
