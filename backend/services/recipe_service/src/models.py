"""
Модели данных для recipe-service
Автономная реализация без зависимостей от других сервисов
"""

from sqlalchemy import (
    String, Text, Integer, ForeignKey, Boolean, DateTime, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy import TypeDecorator
from uuid import UUID as UUIDType, uuid4
import typing as t
from datetime import datetime


class UUIDTypeDecorator(TypeDecorator):
    """
    Декоратор типа для совместимости UUID между SQLite и PostgreSQL
    В SQLite хранит как строку, в PostgreSQL как нативный UUID
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            return UUIDType(value)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей recipe-service"""
    pass


class TimestampMixin:
    """Миксин для добавления временных меток"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment='Время создания записи'
    )

    updated_at: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment='Время последнего обновления'
    )


class UUIDPrimaryKeyMixin:
    """Миксин для добавления UUID первичного ключа"""
    id: Mapped[UUIDType] = mapped_column(
        UUIDTypeDecorator(),
        default=uuid4,
        primary_key=True,
        index=True,
        comment='Уникальный идентификатор'
    )


class StatusMixin:
    """Миксин для добавления статуса активности"""
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment='Флаг активности записи'
    )


class SoftDeleteMixin:
    """Миксин для мягкого удаления (soft delete)"""
    deleted_at: Mapped[t.Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment='Время удаления (мягкое удаление)'
    )

    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        comment='Флаг удаления'
    )


class BaseModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, StatusMixin):
    """Базовая модель для recipe-service"""
    __abstract__ = True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"


class Recipe(BaseModel, SoftDeleteMixin):
    """Модель рецепта"""
    __tablename__ = "recipes"

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

    difficulty: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default='средне',
        comment='Сложность приготовления (легко/средне/сложно)'
    )

    servings: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment='Количество порций'
    )

    # Храним только ID автора (без ForeignKey на другой сервис)
    author_id: Mapped[str] = mapped_column(
        UUIDTypeDecorator(),
        nullable=False,
        index=True,
        comment='ID автора рецепта (ссылка на user-service)'
    )

    # Связи внутри recipe-service
    ingredients = relationship(
        "Ingredient",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )
    steps = relationship(
        "RecipeStep",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )


class Ingredient(BaseModel):
    """Модель ингредиента рецепта"""
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


class Category(BaseModel):
    """Модель категории рецептов"""
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
    """Таблица связи рецептов и категорий"""
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


class Rating(BaseModel):
    """Модель рейтинга рецепта"""
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
