"""
Сервисный слой для работы с рецептами
Обрабатывает бизнес-логику и использует репозиторий для работы с данными
"""

from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.services.recipe_service.models.models_recipe import Recipe
from backend.services.recipe_service.src.repository.recipe_repo import (
    RecipeRepository)
from backend.services.recipe_service.src.repository.recipe_step_repo import (
    RecipeStepRepository)
from backend.services.recipe_service.src.repository.rating_repo import (
    RatingRepository)
from backend.services.recipe_service.src.repository.category_repo import (
    CategoryRepository)
from backend.services.recipe_service.src.repository.ingredient_repo import (
    IngredientRepository)
from backend.services.recipe_service.schemas.schemas import (
    RecipeCreate,
    RecipeUpdate,
    RecipeResponse,
    RecipeSearchParams,
    ReviewCreate)


class RecipeService:
    """Сервис для работы с рецептами"""

    def __init__(self, db: Session):
        self.recipe_repo = RecipeRepository(db)
        self.ingredient_repo = IngredientRepository(db)
        self.step_repo = RecipeStepRepository(db)
        self.category_repo = CategoryRepository(db)
        self.rating_repo = RatingRepository(db)

    def create_recipe(
        self,
        recipe_data: RecipeCreate,
        author_id: UUID
    ) -> RecipeResponse:
        """Создание нового рецепта"""
        # Преобразуем данные схемы в словарь для репозитория
        recipe_dict = recipe_data.model_dump()
        recipe_dict['author_id'] = author_id

        # Создаем рецепт
        recipe = self.recipe_repo.create_recipe(recipe_dict)

        # Создаем ингредиенты
        for ingredient_name in recipe_data.ingredients:
            ingredient_data = {
                'recipe_id': recipe.id,
                'name': ingredient_name,
                'quantity': None
            }
            self.ingredient_repo.create_ingredient(ingredient_data)

        # Создаем шаги приготовления
        for i, instruction in enumerate(recipe_data.instructions, 1):
            step_data = {
                'recipe_id': recipe.id,
                'step_number': i,
                'description': instruction
            }
            self.step_repo.create_step(step_data)

        return self._recipe_to_response(recipe)

    def get_recipe(self, recipe_id: UUID) -> RecipeResponse:
        """Получение рецепта по ID"""
        recipe = self.recipe_repo.get_recipe_by_id(recipe_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Рецепт не найден"
            )
        return self._recipe_to_response(recipe)

    def get_recipes_list(
        self,
        search_params: RecipeSearchParams
    ) -> List[RecipeResponse]:
        """Получение списка рецептов с фильтрацией"""
        recipes = self.recipe_repo.get_recipes_list(
            skip=search_params.skip,
            limit=search_params.limit,
            search=search_params.search,
            min_cooking_time=None,
            max_cooking_time=search_params.max_cooking_time
        )
        return [self._recipe_to_response(recipe) for recipe in recipes]

    def update_recipe(
        self,
        recipe_id: UUID,
        update_data: RecipeUpdate,
        author_id: UUID
    ) -> RecipeResponse:
        """Обновление рецепта"""
        # Проверяем существование рецепта и права автора
        recipe = self.recipe_repo.get_recipe_by_id(recipe_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Рецепт не найден"
            )

        if recipe.author_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для изменения рецепта"
            )

        # Обновляем рецепт
        update_dict = {k: v for k,
                       v in update_data.model_dump().items() if v is not None}
        updated_recipe = self.recipe_repo.update_recipe(recipe_id, update_dict)

        if not updated_recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Рецепт не найден"
            )

        return self._recipe_to_response(updated_recipe)

    def delete_recipe(self, recipe_id: UUID, author_id: UUID) -> bool:
        """Удаление рецепта"""
        # Проверяем существование рецепта и права автора
        recipe = self.recipe_repo.get_recipe_by_id(recipe_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Рецепт не найден"
            )

        if recipe.author_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для удаления рецепта"
            )

        return self.recipe_repo.delete_recipe(recipe_id)

    def add_review(
        self,
        review_data: ReviewCreate,
        author_id: UUID
    ) -> Dict[str, Any]:
        """Добавление отзыва к рецепту"""
        # Проверяем существование рецепта
        recipe = self.recipe_repo.get_recipe_by_id(review_data.recipe_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Рецепт не найден"
            )

        # Проверяем, не оставлял ли пользователь уже отзыв
        existing_rating = self.rating_repo.get_rating_by_user_and_recipe(
            author_id, review_data.recipe_id
        )

        if existing_rating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы уже оставили отзыв на этот рецепт"
            )

        # Создаем отзыв
        rating_data = {
            'recipe_id': review_data.recipe_id,
            'user_id': author_id,
            'value': review_data.rating,
            'comment': review_data.comment
        }

        rating = self.rating_repo.create_rating(rating_data)

        return {
            "message": "Отзыв успешно добавлен",
            "rating_id": rating.id
        }

    def get_recipe_rating(self, recipe_id: UUID) -> Dict[str, Any]:
        """Получение рейтинга рецепта"""
        recipe = self.recipe_repo.get_recipe_by_id(recipe_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Рецепт не найден"
            )

        avg_rating = self.rating_repo.get_average_rating(recipe_id)
        ratings_count = self.rating_repo.get_ratings_count(recipe_id)

        return {
            "recipe_id": recipe_id,
            "average_rating": round(avg_rating, 2),
            "ratings_count": ratings_count
        }

    def _recipe_to_response(self, recipe: Recipe) -> RecipeResponse:
        """Преобразование модели рецепта в схему ответа"""
        # Получаем дополнительные данные
        ingredients = [ingredient.name for ingredient in recipe.ingredients]
        instructions = [step.description for step in recipe.steps]

        # Получаем рейтинг
        avg_rating = self.rating_repo.get_average_rating(recipe.id)
        ratings_count = self.rating_repo.get_ratings_count(recipe.id)

        return RecipeResponse(
            id=recipe.id,
            title=recipe.title,
            description=recipe.description,
            cooking_time=recipe.cooking_time,
            difficulty=recipe.difficulty if hasattr(
                recipe, 'difficulty') else 'средне',
            servings=recipe.servings,
            ingredients=ingredients,
            instructions=instructions,
            author_id=recipe.author_id,
            rating=round(avg_rating, 2) if avg_rating else None,
            review_count=ratings_count,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
            is_active=recipe.is_active
        )
