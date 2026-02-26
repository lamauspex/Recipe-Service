"""
Модели данных для recipe-service
"""


from uuid import UUID as UUIDType
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from backend.shared.models.base import BaseModel


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
        String(50),
        nullable=False,
        comment='Название рецепта'
    )

    ingredient: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment='Ингредиенты'
    )

    description: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment='Описание рецепта'
    )
