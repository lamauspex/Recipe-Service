"""
API роутеры для работы с рецептами
"""

from fastapi import status, APIRouter

from backend.service_recipe.src.schemas import (
    RecipeCreate,
    RecipeResponse
)


router = APIRouter(
    prefix="/recipes",
    tags=["Рецепты"]
)


@router.get(
    "/",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый рецепт",
    description="Создание рецепта с указанием автора"
)
async def create_recipe(
    recipe_data: RecipeCreate,
    recipe_service: RecipeService = Depends(get_recipe_service),

):
    """
    Создание нового рецепта
    Сервис возвращает готовый RecipeResponseDTO
    """

    return recipe_service.create_recipe(
        recipe_data,
        current_user.id
    )
