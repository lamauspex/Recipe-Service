"""
Модель категории рецептов
Таблица связи рецептов и категорий
"""

import typing as t
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.services.recipe_service.models.base_recipe import (
    UUIDTypeDecorator, BaseModel)


class Category(BaseModel):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment='Название категории'
    )

    description: Mapped[t.Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='Описание категории'
    )


class RecipeCategory(BaseModel):
    __tablename__ = "recipe_categories"

    recipe_id: Mapped[str] = mapped_column(
        UUIDTypeDecorator(),
        ForeignKey("recipes.id"),
        primary_key=True,
        comment='ID рецепта'
    )

    category_id: Mapped[str] = mapped_column(
        UUIDTypeDecorator(),
        ForeignKey("categories.id"),
        primary_key=True,
        comment='ID категории'
    )
