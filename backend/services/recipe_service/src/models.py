"""
Шаблон моделей для новых сервисов
Показывает, как использовать общие базовые классы
"""

from sqlalchemy import ForeignKeyConstraint, String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import typing as t

from backend.database.models import BaseModel, UserMixin, SoftDeleteMixin


# Пример модели для сервиса рецептов
class Recipe(BaseModel, SoftDeleteMixin):
    """Модель рецепта"""

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

    servings: Mapped[int] = mapped_column(
        Integer,
        default=1,
        comment='Количество порций'
    )

    # Связь с пользователем (автором рецепта)
    author_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment='ID автора рецепта'
    )

    # Связи
    author = relationship("User", backref="recipes")
    ingredients = relationship(
        "Ingredient", back_populates="recipe", cascade="all, delete-orphan")
    steps = relationship("RecipeStep", back_populates="recipe",
                         cascade="all, delete-orphan")
    comments = relationship(
        "Comment", back_populates="recipe", cascade="all, delete-orphan")


class Ingredient(BaseModel):
    """Модель ингредиента рецепта"""

    recipe_id: Mapped[str] = mapped_column(
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
        comment='Количество (например: "200 г", "1 шт"'
    )

    # Связь с рецептом
    recipe = relationship("Recipe", back_populates="ingredients")


class RecipeStep(BaseModel):
    """Модель шага приготовления рецепта"""

    recipe_id: Mapped[str] = mapped_column(
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
    recipe = relationship("Recipe", back_populates="steps")


# Пример модели для сервиса комментариев
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


# Пример модели для сервиса категорий
class Category(BaseModel):
    """Модель категории рецептов"""

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

    # Связь многие-ко-многим с рецептами
    recipes = relationship(
        "Recipe", secondary="recipe_categories", backref="categories")


# Таблица связи для многие-ко-многим
class RecipeCategory(BaseModel):
    """Таблица связи рецептов и категорий"""

    recipe_id: Mapped[str] = mapped_column(
        ForeignKey("recipes.id"),
        primary_key=True,
        comment='ID рецепта'
    )

    category_id: Mapped[str] = mapped_column(
        ForeignKey("categories.id"),
        primary_key=True,
        comment='ID категории'
    )


# Пример модели для сервиса лайков/рейтингов
class Rating(BaseModel, UserMixin):
    """Модель рейтинга рецепта"""

    recipe_id: Mapped[str] = mapped_column(
        ForeignKey("recipes.id"),
        nullable=False,
        index=True,
        comment='ID рецепта'
    )

    value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Значение рейтинга (1-5)'
    )

    # Уникальный индекс для предотвращения дублирования оценок
    __table_args__ = (
        ForeignKeyConstraint(['recipe_id'], ['recipes.id']),
        ForeignKeyConstraint(['user_id'], ['users.id']),
    )
