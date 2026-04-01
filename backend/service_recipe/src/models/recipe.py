"""
Модели данных для Recipe_Service
"""


from uuid import UUID as UUIDType
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from backend.shared.models.base_model import BaseModel


class Recipe(BaseModel):
    """Модель рецепта"""

    user_id: Mapped[UUIDType] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=True,
        index=True,
        comment='ID пользователя (если пользователь существует)'
    )

    name_recipe: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment='Название рецепта'
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment='Описание рецепта'
    )

    ingredients = relationship(
        "Ingredient",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )
