"""
Модель ингредиента рецепта
"""

import typing as t
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.services.recipe_service.models.base_recipe import (
    UUIDTypeDecorator, BaseModel)


class Ingredient(BaseModel):
    __tablename__ = "ingredients"

    recipe_id: Mapped[str] = mapped_column(
        UUIDTypeDecorator(),
        ForeignKey("recipes.id"),
        nullable=False,
        index=True,
        comment='ID рецепта'
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment='Название ингредиента'
    )

    quantity: Mapped[t.Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment='Количество (например: "200 г", "1 шт")'
    )

    # Связь с рецептом
    recipe = relationship(
        "Recipe",
        back_populates="ingredients"
    )
