"""
Модели данных для recipe-service
"""

import typing as t
from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.services.recipe_service.models.base_recipe import (
    UUIDTypeDecorator, BaseModel, SoftDeleteMixin)


class Recipe(BaseModel, SoftDeleteMixin):
    """Модель рецепта"""
    __tablename__ = "recipes"

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment='Название рецепта'
    )

    description: Mapped[t.Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='Описание рецепта'
    )

    cooking_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Время приготовления в минутах'
    )

    difficulty: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default='средне',
        comment='Сложность приготовления (легко/средне/сложно)'
    )

    servings: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment='Количество порций'
    )

    # Храним только ID автора (без ForeignKey на другой сервис)
    author_id: Mapped[str] = mapped_column(
        UUIDTypeDecorator(),
        nullable=False,
        index=True,
        comment='ID автора рецепта (ссылка на user-service)'
    )

    # Связи внутри recipe-service
    ingredients = relationship(
        "Ingredient",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )
    steps = relationship(
        "RecipeStep",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )
