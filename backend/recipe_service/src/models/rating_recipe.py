"""
Модель рейтинга рецепта
"""

import typing as t
from sqlalchemy import Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.services.recipe_service.models.base_recipe import (
    UUIDTypeDecorator, BaseModel)


class Rating(BaseModel):

    __tablename__ = "ratings"

    recipe_id: Mapped[str] = mapped_column(
        UUIDTypeDecorator(),
        ForeignKey("recipes.id"),
        nullable=False,
        index=True,
        comment='ID рецепта'
    )

    user_id: Mapped[str] = mapped_column(
        UUIDTypeDecorator(),
        nullable=False,
        index=True,
        comment='ID пользователя (ссылка на user-service)'
    )

    value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Значение рейтинга (1-5)'
    )

    comment: Mapped[t.Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='Текст отзыва'
    )

    # Связь с рецептом
    recipe = relationship("Recipe")

    # Уникальный индекс для предотвращения дублирования оценок
    __table_args__ = (
        # Уникальный индекс на пару (recipe_id, user_id)
        # ForeignKeyConstraint(['recipe_id'], ['recipes.id']),
    )
