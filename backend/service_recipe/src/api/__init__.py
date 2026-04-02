"""
API router module
"""

from fastapi import APIRouter

# Импортируем роутеры
from .create_recipe import router as create_recipe_router

# Создаем главный API router
api_router = APIRouter(prefix="/api/v1")


# Подключаем роутеры с префиксами
api_router.include_router(create_recipe_router, prefix="/recipe")
