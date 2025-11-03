"""
Репозиторий для работы с шагами рецепта
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from backend.services.recipe_service.models.step_recipe import (
    RecipeStep
)


class RecipeStepRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_steps_by_recipe(self, recipe_id: UUID) -> List[RecipeStep]:
        """Получение шагов рецепта"""
        return self.db.query(RecipeStep).filter(
            RecipeStep.recipe_id == recipe_id
        ).order_by(RecipeStep.step_number).all()

    def create_step(self, step_data: Dict[str, Any]) -> RecipeStep:
        """Создание шага рецепта"""
        step = RecipeStep(**step_data)
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        return step

    def update_step(
        self,
        step_id: UUID,
        update_data: Dict[str, Any]
    ) -> Optional[RecipeStep]:
        """Обновление шага рецепта"""
        step = self.db.query(RecipeStep).filter(
            RecipeStep.id == step_id
        ).first()

        if not step:
            return None

        for field, value in update_data.items():
            setattr(step, field, value)

        self.db.commit()
        self.db.refresh(step)
        return step

    def delete_step(self, step_id: UUID) -> bool:
        """Удаление шага рецепта"""
        step = self.db.query(RecipeStep).filter(
            RecipeStep.id == step_id
        ).first()

        if not step:
            return False

        self.db.delete(step)
        self.db.commit()
        return True
