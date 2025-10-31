"""
API роутеры для работы с рецептами
Использует сервисный слой для обработки бизнес-логики
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
import logging
from uuid import UUID

from backend.database.connection import get_db
from backend.services.user_service.src.middleware.jwt_middleware import get_current_active_user
from backend.services.recipe_service.src.schemas import (
    RecipeCreate, RecipeUpdate, RecipeResponse, RecipeSearchParams,
    RecipeListResponse, ReviewCreate
)
from backend.services.recipe_service.src.services.recipe_service import RecipeService


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
    description="Получение списка рецептов с возможностью фильтрации и пагинации"
)
async def get_recipes_list(
    search: str = Query(None, description="Поиск по названию и описанию"),
    difficulty: str = Query(
        None, description="Сложность (легко/средне/сложно)"),
    max_cooking_time: int = Query(
        None, description="Максимальное время приготовления"),
    skip: int = Query(0, ge=0, description="Количество пропущенных элементов"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Количество элементов на странице"),
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

# Создание рецепта


@router.post("/recipes/new", response_model=RecipeOut,
             summary="Добавить рецепт", tags=["Рецепты"]
             )
async def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db)
):
    # Создаем Recipe
    recipe_obj = Recipe(
        name=recipe.name,
        instructions=recipe.instructions,
        author_id=recipe.author_id,
        category=recipe.category
    )
    session.add(recipe_obj)
    await session.commit()
    await session.refresh(recipe_obj)

    # Создаем RecipeIngredient для каждого ингредиента
    for ingredient_data in recipe.ingredients:
        ingredient = await session.execute(
            select(Ingredient).where(Ingredient.id ==
                                     ingredient_data.ingredient_id)
        )
        ingredient = ingredient.scalar_one_or_none()

        if ingredient is None:
            raise HTTPException(
                status_code=400,
                detail=f"Ингредиент с ID '{ingredient_data.ingredient_id}' не найден"
            )

        recipe_ingredient = RecipeIngredient(
            recipe=recipe_obj,
            ingredient=ingredient,
            quantity=ingredient_data.quantity
        )
        session.add(recipe_ingredient)
    await session.commit()

    return RecipeOut(**recipe_obj.dict())

# Получение списка всех рецептов


@router.get("/recipes/search/list", response_model=List[RecipeOut], summary="Список рецептов", tags=["Рецепты"])
async def get_recipes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Recipe).options(joinedload(Recipe.ingredients)))
    recipes = result.scalars().all()
    return recipes

# Удаление рецепта


@router.delete("/recipes/{recipe_id}", summary="Удаление рецепта", tags=["Рецепты"])
async def delete_recipe(recipe_id: int, session: AsyncSession = Depends(get_session)):
    # Проверка существования рецепта
    recipe = await session.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = recipe.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    # Удаление связанных записей в recipe_ingredients
    await session.execute(delete(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id))

    # Удаление рецепта
    await session.delete(recipe)
    await session.commit()
    return {"message": "Рецепт удален"}

# Поиск по категоориям


@router.get("/recipes/search/by_category", response_model=List[RecipeOut], summary="Категория", tags=["Поиск"])
async def get_category(category: str = Query(..., description="Название категории"), session: AsyncSession = Depends(get_session)):
    query = select(Recipe).where(Recipe.category == category)
    result = await session.execute(query)
    recipes = result.scalars().all()
    return recipes

# Поиск по названию


@router.get("/recipes/search/by_name", response_model=List[RecipeOut], summary="Название", tags=["Поиск"])
async def get_name(name: str = Query(..., description="Название блюда"), session: AsyncSession = Depends(get_session)):
    query = select(Recipe).where(Recipe.name == name)
    result = await session.execute(query)
    recipes = result.scalars().all()
    return recipes
