"""
Репозиторий для работы с категориями
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from backend.services.recipe_service.models.category_recipe import (
    Category, RecipeCategory)


class CategoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all_categories(self) -> List[Category]:
        """Получение всех категорий"""
        return self.db.query(Category).all()

    def get_category_by_id(self, category_id: UUID) -> Optional[Category]:
        """Получение категории по ID"""
        return self.db.query(Category).filter(
            Category.id == category_id
        ).first()

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Получение категории по имени"""
        return self.db.query(Category).filter(
            Category.name == name
        ).first()

    def create_category(self, category_data: Dict[str, Any]) -> Category:
        """Создание категории"""
        category = Category(**category_data)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def add_recipe_to_category(
        self,
        recipe_id: UUID,
        category_id: UUID
    ) -> bool:
        """Добавление рецепта в категорию"""
        # Проверяем существование связи
        existing = self.db.query(RecipeCategory).filter(
            RecipeCategory.recipe_id == recipe_id,
            RecipeCategory.category_id == category_id
        ).first()

        if existing:
            return False

        recipe_category = RecipeCategory(
            recipe_id=recipe_id,
            category_id=category_id
        )
        self.db.add(recipe_category)
        self.db.commit()
        return True

    def remove_recipe_from_category(
        self,
        recipe_id: UUID,
        category_id: UUID
    ) -> bool:
        """Удаление рецепта из категории"""
        result = self.db.query(RecipeCategory).filter(
            RecipeCategory.recipe_id == recipe_id,
            RecipeCategory.category_id == category_id
        ).delete()

        self.db.commit()
        return result > 0
