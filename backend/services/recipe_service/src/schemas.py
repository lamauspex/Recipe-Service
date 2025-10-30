"""
Схемы Pydantic для recipe-service
Наследуются от базовых схем из backend.database.schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID

from backend.database.schemas import (
    BaseResponse,
    PaginationParams,
    PaginatedResponse
)


class RecipeBase(BaseModel):
    """Базовая схема рецепта"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Название рецепта"
    )
    description: Optional[str] = Field(
        None, description="Описание рецепта"
    )
    cooking_time: int = Field(
        ...,
        ge=1,
        description="Время приготовления в минутах"
    )
    difficulty: str = Field(
        ...,
        pattern="^(легко|средне|сложно)$",
        description="Сложность приготовления"
    )
    servings: int = Field(
        ...,
        ge=1,
        description="Количество порций"
    )


class RecipeCreate(RecipeBase):
    """Схема для создания рецепта"""
    ingredients: List[str] = Field(
        ...,
        min_items=1,
        description="Список ингредиентов"
    )
    instructions: List[str] = Field(
        ...,
        min_items=1,
        description="Шаги приготовления"
    )


class RecipeUpdate(BaseModel):
    """Схема для обновления рецепта"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    cooking_time: Optional[int] = Field(None, ge=1)
    difficulty: Optional[str] = Field(None, pattern="^(легко|средне|сложно)$")
    servings: Optional[int] = Field(None, ge=1)
    ingredients: Optional[List[str]] = Field(None, min_items=1)
    instructions: Optional[List[str]] = Field(None, min_items=1)


class RecipeResponse(RecipeBase, BaseResponse):
    """Схема ответа с данными рецепта"""
    ingredients: List[str] = Field(description="Список ингредиентов")
    instructions: List[str] = Field(description="Шаги приготовления")
    author_id: UUID = Field(description="ID автора рецепта")
    rating: Optional[float] = Field(
        None, ge=0, le=5, description="Рейтинг рецепта")
    review_count: int = Field(default=0, description="Количество отзывов")


class RecipeSearchParams(PaginationParams):
    """Параметры поиска рецептов"""
    search: Optional[str] = Field(
        None, description="Поиск по названию и описанию")
    difficulty: Optional[str] = Field(None, pattern="^(легко|средне|сложно)$")
    max_cooking_time: Optional[int] = Field(
        None, ge=1, description="Максимальное время приготовления")
    min_rating: Optional[float] = Field(
        None, ge=0, le=5, description="Минимальный рейтинг")


class RecipeListResponse(PaginatedResponse[RecipeResponse]):
    """Схема списка рецептов"""
    pass


class ReviewBase(BaseModel):
    """Базовая схема отзыва"""
    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Оценка от 1 до 5"
    )
    comment: Optional[str] = Field(
        None,
        max_length=1000,
        description="Текст отзыва"
    )


class ReviewCreate(ReviewBase):
    """Схема для создания отзыва"""
    recipe_id: UUID = Field(..., description="ID рецепта")


class ReviewResponse(ReviewBase, BaseResponse):
    """Схема ответа с данными отзыва"""
    recipe_id: UUID = Field(description="ID рецепта")
    author_id: UUID = Field(description="ID автора отзыва")


# Дженерик схемы для использования в других сервисах
RecipePaginatedResponse = PaginatedResponse[RecipeResponse]
ReviewPaginatedResponse = PaginatedResponse[ReviewResponse]


__all__ = [
    'RecipeBase',
    'RecipeCreate',
    'RecipeUpdate',
    'RecipeResponse',
    'RecipeSearchParams',
    'RecipeListResponse',
    'ReviewBase',
    'ReviewCreate',
    'ReviewResponse',
    'RecipePaginatedResponse',
    'ReviewPaginatedResponse'
]
