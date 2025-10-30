
from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import typing as t

from backend.database.models import BaseModel, UserMixin, SoftDeleteMixin


class Comment(BaseModel, UserMixin, SoftDeleteMixin):
    """Модель комментария"""

    recipe_id: Mapped[str] = mapped_column(
        ForeignKey("recipes.id"),
        nullable=False,
        index=True,
        comment='ID рецепта'
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment='Текст комментария'
    )

    parent_id: Mapped[t.Optional[str]] = mapped_column(
        ForeignKey("comments.id"),
        nullable=True,
        comment='ID родительского комментария (для вложенных комментариев)'
    )

    # Связи
    recipe = relationship("Recipe", back_populates="comments")
    author = relationship("User", backref="comments")

    # Для вложенных комментариев
    parent = relationship(
        "Comment", remote_side="Comment.id", backref="replies")
