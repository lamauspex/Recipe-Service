"""
Репозиторий для работы с рейтингами
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Dict, Any
from uuid import UUID

from backend.services.recipe_service.models.rating_recipe import (
    Rating
)


class RatingRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_rating_by_user_and_recipe(
        self,
        user_id: UUID,
        recipe_id: UUID
    ) -> Optional[Rating]:
        """Получение оценки пользователя для рецепта"""
        return self.db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.recipe_id == recipe_id
        ).first()

    def create_rating(self, rating_data: Dict[str, Any]) -> Rating:
        """Создание оценки"""
        rating = Rating(**rating_data)
        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)
        return rating

    def update_rating(
        self,
        rating_id: UUID,
        update_data: Dict[str, Any]
    ) -> Optional[Rating]:
        """Обновление оценки"""
        rating = self.db.query(Rating).filter(Rating.id == rating_id).first()

        if not rating:
            return None

        for field, value in update_data.items():
            setattr(rating, field, value)

        self.db.commit()
        self.db.refresh(rating)
        return rating

    def get_average_rating(self, recipe_id: UUID) -> float:
        """Получение среднего рейтинга рецепта"""
        result = self.db.query(func.avg(Rating.value)).filter(
            Rating.recipe_id == recipe_id
        ).scalar()

        return result or 0.0

    def get_ratings_count(self, recipe_id: UUID) -> int:
        """Получение количества оценок рецепта"""
        return self.db.query(func.count(Rating.id)).filter(
            Rating.recipe_id == recipe_id
        ).scalar()
