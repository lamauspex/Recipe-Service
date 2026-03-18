"""
Схемы для входящих запросов API рецептов
"""


from pydantic import ConfigDict, Field

from backend.service_recipe.src.schemas import (
    TitleValidatedModel,
    IngredientSchema,
    DescriptionValidatedModel
)


class RecipeCreate(
    TitleValidatedModel,
    DescriptionValidatedModel
):
    """
    Модель для создания нового рецепта

    Наследует:
    - TitleValidatedModel: валидация названия
    - DescriptionValidatedModel: валидация описания

    Attributes:
        name_recipe: Название рецепта (обязательно, 2-50 символов)
        description: Описание рецепта (обязательно, 5-500 символов)
        ingredients: Список ингредиентов (минимум 1)

    Example:
        >>> recipe = RecipeCreate(
        ...     name_recipe="Борщ",
        ...     description="Традиционный украинский борщ со сметаной",
        ...     ingredients=[
        ...         {"name": "Свекла", "quantity": "300", "unit": "г"},
        ...         {"name": "Капуста", "quantity": "200", "unit": "г"}
        ...     ]
        ... )
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name_recipe": "Борщ",
                "description": "Традиционный украинский борщ со сметаной",
                "ingredients": [
                    {
                        "name": "Свекла",
                        "quantity": "300",
                        "unit": "г"
                    },
                    {
                        "name": "Капуста",
                        "quantity": "200",
                        "unit": "г"
                    }
                ]
            }
        }
    )

    ingredients: list[IngredientSchema] = Field(
        ...,
        description="Список ингредиентов рецепта"
    )
