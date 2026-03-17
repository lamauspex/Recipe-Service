
from backend.service_recipe.src.schemas.base.base import TitleValidatedModel


class RecipeCreate(TitleValidatedModel):
    """
    Модель для создания нового рецепта
    Наследует:
    - TitleValidatedModel: валидация названия
    """
    ingredient: str
    description: str
