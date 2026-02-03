
"""
Репозиторий для работы с ингредиентами
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from backend.services.recipe_service.models.ingredient_recipe import (
    Ingredient
)


class IngredientRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_ingredients_by_recipe(self, recipe_id: UUID) -> List[Ingredient]:
        """Получение ингредиентов рецепта"""
        return self.db.query(Ingredient).filter(
            Ingredient.recipe_id == recipe_id
        ).all()

    def create_ingredient(self, ingredient_data: Dict[str, Any]) -> Ingredient:
        """Создание ингредиента"""
        ingredient = Ingredient(**ingredient_data)
        self.db.add(ingredient)
        self.db.commit()
        self.db.refresh(ingredient)
        return ingredient

    def update_ingredient(
        self,
        ingredient_id: UUID,
        update_data: Dict[str, Any]
    ) -> Optional[Ingredient]:
        """Обновление ингредиента"""
        ingredient = self.db.query(Ingredient).filter(
            Ingredient.id == ingredient_id
        ).first()

        if not ingredient:
            return None

        for field, value in update_data.items():
            setattr(ingredient, field, value)

        self.db.commit()
        self.db.refresh(ingredient)
        return ingredient

    def delete_ingredient(self, ingredient_id: UUID) -> bool:
        """Удаление ингредиента"""
        ingredient = self.db.query(Ingredient).filter(
            Ingredient.id == ingredient_id
        ).first()

        if not ingredient:
            return False

        self.db.delete(ingredient)
        self.db.commit()
        return True
