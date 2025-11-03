
"""
Модели данных для recipe-service
"""

from sqlalchemy import Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.services.recipe_service.models.base_recipe import (
    UUIDTypeDecorator, BaseModel)


class RecipeStep(BaseModel):
    """Модель шага приготовления рецепта"""
    __tablename__ = "recipe_steps"

    recipe_id: Mapped[str] = mapped_column(
        UUIDTypeDecorator(),
        ForeignKey("recipes.id"),
        nullable=False,
        index=True,
        comment='ID рецепта'
    )

    step_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Номер шага'
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment='Описание шага'
    )

    # Связь с рецептом
    recipe = relationship(
        "Recipe",
        back_populates="steps"
    )
