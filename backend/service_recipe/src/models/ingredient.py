"""
Модель данных для Recipe_Service
"""

from uuid import UUID as UUIDType
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from backend.shared.models.base_model import BaseModel


class Ingredient(BaseModel):
    """Модель ингредиента рецепта"""

    recipe_id: Mapped[UUIDType] = mapped_column(
        ForeignKey(
            "recipes.id",
            ondelete="CASCADE"
        ),
        nullable=True,
        index=True,
        comment='ID рецепта'
    )

    ingredient: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment='Ингредиенты'
    )

    quantity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment='Количество'
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment='Единица измерения'
    )

    recipe = relationship(
        "Recipe",
        back_populates="ingredients"
    )
