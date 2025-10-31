"""
Репозиторий для работы с рецептами и связанными сущностями
"""
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, and_, or_, func
from typing import List, Optional, Dict, Any
from uuid import UUID

from backend.services.recipe_service.src.models import (
    Recipe, Ingredient, RecipeStep, Category, RecipeCategory, Rating
)


class RecipeRepository:
    """Репозиторий для работы с рецептами"""

    def __init__(self, db: Session):
        self.db = db

    def get_recipe_by_id(self, recipe_id: UUID) -> Optional[Recipe]:
        """Получение рецепта по ID с полными данными"""
        return self.db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.is_deleted.is_(False)
        ).options(
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
            selectinload(Recipe.author)
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

    def create_recipe(self, recipe_data: Dict[str, Any]) -> Recipe:
        """Создание нового рецепта"""
        recipe = Recipe(**recipe_data)
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        return recipe

    def update_recipe(self, recipe_id: UUID, update_data: Dict[str, Any]) -> Optional[Recipe]:
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


class IngredientRepository:
    """Репозиторий для работы с ингредиентами"""

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

    def update_ingredient(self, ingredient_id: UUID, update_data: Dict[str, Any]) -> Optional[Ingredient]:
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


class RecipeStepRepository:
    """Репозиторий для работы с шагами рецепта"""

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

    def update_step(self, step_id: UUID, update_data: Dict[str, Any]) -> Optional[RecipeStep]:
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


class CategoryRepository:
    """Репозиторий для работы с категориями"""

    def __init__(self, db: Session):
        self.db = db

    def get_all_categories(self) -> List[Category]:
        """Получение всех категорий"""
        return self.db.query(Category).all()

    def get_category_by_id(self, category_id: UUID) -> Optional[Category]:
        """Получение категории по ID"""
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Получение категории по имени"""
        return self.db.query(Category).filter(Category.name == name).first()

    def create_category(self, category_data: Dict[str, Any]) -> Category:
        """Создание категории"""
        category = Category(**category_data)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def add_recipe_to_category(self, recipe_id: UUID, category_id: UUID) -> bool:
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

    def remove_recipe_from_category(self, recipe_id: UUID, category_id: UUID) -> bool:
        """Удаление рецепта из категории"""
        result = self.db.query(RecipeCategory).filter(
            RecipeCategory.recipe_id == recipe_id,
            RecipeCategory.category_id == category_id
        ).delete()

        self.db.commit()
        return result > 0


class RatingRepository:
    """Репозиторий для работы с рейтингами"""

    def __init__(self, db: Session):
        self.db = db

    def get_rating_by_user_and_recipe(self, user_id: UUID, recipe_id: UUID) -> Optional[Rating]:
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

    def update_rating(self, rating_id: UUID, update_data: Dict[str, Any]) -> Optional[Rating]:
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
