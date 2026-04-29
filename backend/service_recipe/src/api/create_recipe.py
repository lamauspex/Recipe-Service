"""
API роутеры для работы с рецептами
"""

from fastapi import status, APIRouter, Depends

from backend.service_recipe.src.infrastructure import get_message_publisher
from backend.service_recipe.src.service import (
    MessagePublisher,
    RecipeService
)
from backend.service_recipe.src.schemas import (
    RecipeCreate,
    RecipeResponse
)
from backend.service_recipe.src.infrastructure import (
    get_current_user,
    get_recipe_service
)


router = APIRouter(
    prefix="/recipes",
    tags=["Recipe_Service"]
)


@router.post(
    "/",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый рецепт",
    description="Создание рецепта с авторизованным пользователем"
)
async def create_recipe(
    recipe_data: RecipeCreate,
    current_user: dict = Depends(get_current_user),
    recipe_service: RecipeService = Depends(get_recipe_service),
    publisher: MessagePublisher = Depends(get_message_publisher)
):
    """
    Создание нового рецепта
    Требует JWT токен в заголовке Authorization: Bearer <token>
    Возвращает созданный рецепт
    """
    # Создаём рецепт через сервис
    recipe = recipe_service.create_recipe(
        recipe_data=recipe_data,
        user_id=current_user["user_id"]
    )

    # Публикуем событие в RabbitMQ
    await publisher.publish_recipe_created({
        "recipe_id": str(recipe.id),
        "user_id": current_user["user_id"],
        "recipe_name": recipe_data.name_recipe,
        "event": "recipe_created"
    })

    return recipe
