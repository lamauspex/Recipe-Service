"""
Базовые схемы с валидацией для переиспользования
"""


from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.service_recipe.src.schemas.base.validated import (
    TitleValidator,
    DescriptionValidator
)


class TitleValidatedModel(BaseModel):
    """
    Базовая схема с валидацией имени

    Предоставляет поле name_recipe с встроенной валидацией:
    - Минимальная длина: 2 символа
    - Максимальная длина: 150 символов
    - Разрешены: буквы, цифры, дефис, подчёркивание

    Наследуется в RecipeCreate и других схемах с названием.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"name_recipe": "Борщ"},
                {"name_recipe": "Оливье-2019"},
            ]
        }
    )

    name_recipe: str = Field(..., description="Название рецепта")

    @field_validator('name_recipe')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Валидация названия рецепта

        Проверяет название на соответствие требованиям:
            - Длина в допустимых пределах
            - Корректные символы

        Raises:
            ValueError: Если название не прошло валидацию
        """

        is_valid, errors = TitleValidator.validate(v)

        if not is_valid:
            raise ValueError('. '.join(errors))
        return v


class DescriptionValidatedModel(BaseModel):
    """
    Базовая схема с валидацией описания

    Предоставляет поле description с встроенной валидацией:
    - Минимальная длина: 5 символов
    - Максимальная длина: 500 символов

    Наследуется в RecipeCreate и других схемах с описанием.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"description": "Вкусный домашний борщ"},
                {"description": "Классический салат оливье с горошком"},
            ]
        }
    )

    description: str = Field(..., description="Описание рецепта")

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """
        Валидация описания рецепта

        Проверяет описание на соответствие требованиям:
        - Длина в допустимых пределах

        Raises:
            ValueError: Если описание не прошло валидацию
        """

        is_valid, errors = DescriptionValidator.validate(v)

        if not is_valid:
            raise ValueError('. '.join(errors))
        return v
