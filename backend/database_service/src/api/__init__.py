"""
API router module
"""
from fastapi import APIRouter
from .routers import router as db_router

# Создаем главный API router
api_router = APIRouter(prefix="/api/v1")

# Подключаем все роутеры с префиксами
api_router.include_router(db_router, prefix="/db")
