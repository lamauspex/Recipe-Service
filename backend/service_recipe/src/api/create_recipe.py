"""
API роутеры для работы с рецептами
"""

from datetime import datetime, timezone
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
from backend.shared.logging.logger import get_logger


logger = get_logger(__name__).bind(
    layer="api",
    service="recipe"
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
    logger.info(
        "→ Recipe creation started",
        user_id=current_user.get("user_id"),
        recipe_name=recipe_data.name_recipe
    )

    # Создаём рецепт через сервис
    recipe = recipe_service.create_recipe(
        recipe_data=recipe_data,
        user_id=current_user["user_id"]
    )

    logger.info(
        "✓ Recipe created successfully",
        recipe_id=str(recipe.id),
        user_id=current_user["user_id"]
    )

    # Публикуем событие в RabbitMQ
    await publisher.publish_recipe_created({
        "type": "recipe.created",
        "recipe_id": str(recipe.id),
        "payload": {
            "id": str(recipe.id),
            "title": recipe_data.name_recipe,
            "description": recipe_data.description
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return recipe
