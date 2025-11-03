"""
API роутеры для работы с рецептами
Использует сервисный слой для обработки бизнес-логики
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
import logging
from uuid import UUID

from backend.services.recipe_service.src.database.connection import get_db
from backend.services.user_service.src.middleware.jwt_middleware import (
    get_current_active_user)
from backend.services.recipe_service.schemas.schemas import (
    RecipeCreate, RecipeUpdate, RecipeResponse,
    RecipeSearchParams, ReviewCreate)
from backend.services.recipe_service.src.services.recipe_service import (
    RecipeService)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recipes", tags=["Рецепты"])


@router.post(
    "/",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый рецепт",
    description="Создание рецепта с указанием автора"
)
async def create_recipe(
    recipe_data: RecipeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Создание нового рецепта"""
    service = RecipeService(db)
    return service.create_recipe(recipe_data, current_user.id)


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Получить рецепт по ID",
    description="Получение полной информации о рецепте по его идентификатору"
)
async def get_recipe(
    recipe_id: UUID,
    db: Session = Depends(get_db)
):
    """Получение рецепта по ID"""
    service = RecipeService(db)
    return service.get_recipe(recipe_id)


@router.get(
    "/",
    response_model=List[RecipeResponse],
    summary="Получить список рецептов",
    description="Получение списка рецептов (фильтрации и пагинации)"
)
async def get_recipes_list(
    search: str = Query(
        None,
        description="Поиск по названию и описанию"
    ),
    difficulty: str = Query(
        None,
        description="Сложность (легко/средне/сложно)"
    ),
    max_cooking_time: int = Query(
        None,
        description="Максимальное время приготовления"
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Количество пропущенных элементов"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Количество элементов на странице"
    ),
    db: Session = Depends(get_db)
):
    """Получение списка рецептов"""
    search_params = RecipeSearchParams(
        search=search,
        difficulty=difficulty,
        max_cooking_time=max_cooking_time,
        skip=skip,
        limit=limit
    )
    service = RecipeService(db)
    return service.get_recipes_list(search_params)


@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Обновить рецепт",
    description="Обновление данных рецепта автором"
)
async def update_recipe(
    recipe_id: UUID,
    update_data: RecipeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Обновление рецепта"""
    service = RecipeService(db)
    return service.update_recipe(recipe_id, update_data, current_user.id)


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить рецепт",
    description="Мягкое удаление рецепта автором"
)
async def delete_recipe(
    recipe_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Удаление рецепта"""
    service = RecipeService(db)
    service.delete_recipe(recipe_id, current_user.id)
    return None


@router.post(
    "/{recipe_id}/reviews",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить отзыв к рецепту",
    description="Добавление отзыва с рейтингом к рецепту"
)
async def add_review(
    recipe_id: UUID,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Добавление отзыва к рецепту"""
    service = RecipeService(db)
    return service.add_review(review_data, current_user.id)


@router.get(
    "/{recipe_id}/rating",
    summary="Получить рейтинг рецепта",
    description="Получение среднего рейтинга и количества отзывов"
)
async def get_recipe_rating(
    recipe_id: UUID,
    db: Session = Depends(get_db)
):
    """Получение рейтинга рецепта"""
    service = RecipeService(db)
    return service.get_recipe_rating(recipe_id)
