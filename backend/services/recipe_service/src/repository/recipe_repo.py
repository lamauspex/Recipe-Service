"""
Репозиторий для работы с рецептами
"""

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, func
from typing import List, Optional, Dict, Any
from uuid import UUID

from backend.services.recipe_service.models.models_recipe import Recipe
from backend.services.recipe_service.models.category_recipe import Category


class RecipeRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_recipe_by_id(self, recipe_id: UUID) -> Optional[Recipe]:
        """Получение рецепта по ID с полными данными"""
        return self.db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.is_deleted.is_(False)
        ).options(
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps)
        ).first()

    def get_recipes_list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category_id: Optional[UUID] = None,
        author_id: Optional[UUID] = None,
        min_cooking_time: Optional[int] = None,
        max_cooking_time: Optional[int] = None,
        difficulty: Optional[str] = None
    ) -> List[Recipe]:
        """Получение списка рецептов с фильтрацией"""
        query = self.db.query(Recipe).filter(
            Recipe.is_deleted.is_(False)
        )

        if search:
            query = query.filter(
                or_(
                    Recipe.title.ilike(f"%{search}%"),
                    Recipe.description.ilike(f"%{search}%")
                )
            )

        if category_id:
            query = query.join(Recipe.categories).filter(
                Category.id == category_id
            )

        if author_id:
            query = query.filter(Recipe.author_id == author_id)

        if min_cooking_time:
            query = query.filter(Recipe.cooking_time >= min_cooking_time)

        if max_cooking_time:
            query = query.filter(Recipe.cooking_time <= max_cooking_time)

        if difficulty:
            query = query.filter(Recipe.difficulty == difficulty)

        return query.offset(skip).limit(limit).all()

    def create_recipe(
        self,
        recipe_data: Dict[str, Any]
    ) -> Recipe:
        """Создание нового рецепта"""
        recipe = Recipe(**recipe_data)
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        return recipe

    def update_recipe(
        self,
        recipe_id: UUID,
        update_data: Dict[str, Any]
    ) -> Optional[Recipe]:
        """Обновление рецепта"""
        recipe = self.get_recipe_by_id(recipe_id)
        if not recipe:
            return None

        for field, value in update_data.items():
            setattr(recipe, field, value)

        self.db.commit()
        self.db.refresh(recipe)
        return recipe

    def delete_recipe(self, recipe_id: UUID) -> bool:
        """Мягкое удаление рецепта"""
        recipe = self.get_recipe_by_id(recipe_id)
        if not recipe:
            return False

        recipe.is_deleted = True
        recipe.deleted_at = func.now()
        self.db.commit()
        return True

    def get_recipes_count(
        self,
        search: Optional[str] = None,
        category_id: Optional[UUID] = None
    ) -> int:
        """Получение количества рецептов"""
        query = self.db.query(func.count(Recipe.id)).filter(
            Recipe.is_deleted.is_(False)
        )

        if search:
            query = query.filter(
                or_(
                    Recipe.title.ilike(f"%{search}%"),
                    Recipe.description.ilike(f"%{search}%")
                )
            )

        if category_id:
            query = query.join(Recipe.categories).filter(
                Category.id == category_id
            )

        return query.scalar()
