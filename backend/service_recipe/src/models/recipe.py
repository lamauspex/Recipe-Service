"""
Модели данных для Recipe_Service
"""


from uuid import UUID as UUIDType
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from backend.shared.models.base.decorator.type_decorator import (
    UUIDTypeDecorator)
from backend.shared.models.base_model import BaseModel


class Recipe(BaseModel):
    """Модель рецепта"""

    user_id: Mapped[UUIDType] = mapped_column(
        UUIDTypeDecorator(),
        nullable=False,
        index=True,
        comment='ID пользователя'
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
