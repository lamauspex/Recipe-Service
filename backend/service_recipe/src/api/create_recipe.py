"""
API роутеры для работы с рецептами
"""

from fastapi import status

from .base import router


@router.get(
    "/",
    response_model=RecipeResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый рецепт",
    description="Создание рецепта с указанием автора"
)
async def create_recipe(
    recipe_data: RecipeCreate,
    recipe_service: RecipeService = Depends(get_recipe_service),
    current_user=Depends(get_current_active_user)
):
    """Создание нового рецепта"""

    return recipe_service.create_recipe(
        recipe_data,
        current_user.id
    )
