# """
# Фикстуры для тестовых данных рецептов
# """

# import pytest

# from backend.services.recipe_service.src.models import Recipe


# @pytest.fixture
# def recipe_service(db_session):
#     """Фикстура для RecipeService"""
#     # Если есть сервис - импортируем, если нет - создаем базовый
#     try:
#         return RecipeService(db_session)
#     except ImportError:
#         # Создаем базовый сервис для тестов
#         class BasicRecipeService:
#             def __init__(self, db):
#                 self.db = db
#         return BasicRecipeService(db_session)


# @pytest.fixture
# def sample_recipe_data():
#     """Тестовые данные рецепта"""
#     return {
#         "title": "Тестовый рецепт пасты",
#         "description": "Простой и вкусный рецепт пасты",
#         "ingredients": ["макароны 200г", "томатный соус 100мл", "специи"],
#         "instructions": "1. Сварить макароны\n2. Добавить соус\n3. Подавать горячим",
#         "cooking_time": 30,
#         "difficulty": "medium",
#         "servings": 4,
#         "is_published": True
#     }


# @pytest.fixture
# def recipe_data():
#     """Тестовые данные для создания рецепта"""
#     return RecipeCreate(
#         title="Тестовый рецепт",
#         description="Описание тестового рецепта",
#         ingredients=["ингредиент 1", "ингредиент 2"],
#         instructions="Инструкция приготовления",
#         cooking_time=30,
#         difficulty="easy",
#         servings=2
#     )


# @pytest.fixture
# def test_recipe(db_session, test_user):
#     """Фикстура для создания тестового рецепта"""
#     recipe_data = {
#         "title": "Тестовый рецепт",
#         "description": "Тестовое описание",
#         "ingredients": ["тест1", "тест2"],
#         "instructions": "тест инструкция",
#         "cooking_time": 30,
#         "difficulty": "easy",
#         "servings": 2,
#         "author_id": test_user.id,
#         "is_published": True
#     }

#     recipe = Recipe(**recipe_data)
#     db_session.add(recipe)
#     db_session.commit()
#     db_session.refresh(recipe)
#     return recipe


# # Утилитные функции для тестов рецептов
# def create_test_recipe(db_session, author, **kwargs):
#     """Создание тестового рецепта"""
#     default_data = {
#         "title": "Тестовый рецепт",
#         "description": "Тестовое описание рецепта",
#         "ingredients": ["ингредиент 1", "ингредиент 2"],
#         "instructions": "Шаг 1. Приготовить\nШаг 2. Подать",
#         "cooking_time": 30,
#         "difficulty": "medium",
#         "servings": 4,
#         "author_id": author.id,
#         "is_published": True
#     }
#     default_data.update(kwargs)

#     recipe = Recipe(**default_data)
#     db_session.add(recipe)
#     db_session.commit()
#     db_session.refresh(recipe)
#     return recipe


# def cleanup_recipe_data(db_session):
#     """Очистка тестовых данных рецептов"""
#     try:
#         db_session.query(Recipe).delete()
#         db_session.commit()
#     except Exception as e:
#         db_session.rollback()
#         raise e
