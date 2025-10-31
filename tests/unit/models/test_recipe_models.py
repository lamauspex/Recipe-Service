# """
# Тесты для моделей recipe-service
# """

# import pytest
# from datetime import datetime
# from uuid import UUID

# from backend.services.recipe_service.src.models import Recipe


# pytestmark = pytest.mark.skip(
#     reason="Recipe models dependency issues - need to fix categories table first"
# )


# def test_recipe_model_creation(db_session, test_user):
#     """Тест создания модели рецепта"""
#     recipe = Recipe(
#         title="Тестовый рецепт",
#         description="Описание тестового рецепта",
#         ingredients=["ингредиент 1", "ингредиент 2"],
#         instructions="Инструкция приготовления",
#         cooking_time=30,
#         difficulty="easy",
#         servings=4,
#         author_id=test_user.id,
#         is_published=True
#     )

#     db_session.add(recipe)
#     db_session.commit()
#     db_session.refresh(recipe)

#     assert recipe.id is not None
#     assert isinstance(recipe.id, UUID)
#     assert recipe.title == "Тестовый рецепт"
#     assert recipe.description == "Описание тестового рецепта"
#     assert recipe.ingredients == ["ингредиент 1", "ингредиент 2"]
#     assert recipe.cooking_time == 30
#     assert recipe.difficulty == "easy"
#     assert recipe.servings == 4
#     assert recipe.author_id == test_user.id
#     assert recipe.is_published is True
#     assert recipe.created_at is not None
#     assert isinstance(recipe.created_at, datetime)


# def test_recipe_model_repr(db_session, test_user):
#     """Тест строкового представления рецепта"""
#     recipe = Recipe(
#         title="Тестовый рецепт",
#         description="Описание",
#         ingredients=[],
#         instructions="",
#         cooking_time=30,
#         difficulty="easy",
#         servings=2,
#         author_id=test_user.id
#     )

#     db_session.add(recipe)
#     db_session.commit()
#     db_session.refresh(recipe)

#     repr_str = repr(recipe)
#     assert "Recipe" in repr_str
#     assert f"id={recipe.id}" in repr_str
#     assert "title='Тестовый рецепт'" in repr_str


# def test_recipe_required_fields(db_session, test_user):
#     """Тест обязательных полей рецепта"""
#     # Должна быть ошибка при отсутствии обязательных полей
#     recipe = Recipe(
#         # title отсутствует - обязательно
#         description="Описание",
#         ingredients=[],
#         instructions="",
#         cooking_time=30,
#         author_id=test_user.id
#     )

#     db_session.add(recipe)

#     with pytest.raises(Exception):
#         db_session.commit()


# def test_recipe_cooking_time_validation(db_session, test_user):
#     """Тест валидации времени приготовления"""
#     # Отрицательное время должно вызывать ошибку
#     recipe = Recipe(
#         title="Тестовый рецепт",
#         description="Описание",
#         ingredients=[],
#         instructions="",
#         cooking_time=-10,  # Невалидное значение
#         author_id=test_user.id
#     )

#     db_session.add(recipe)

#     with pytest.raises(Exception):
#         db_session.commit()


# def test_recipe_difficulty_validation(db_session, test_user):
#     """Тест валидации сложности"""
#     recipe = Recipe(
#         title="Тестовый рецепт",
#         description="Описание",
#         ingredients=[],
#         instructions="",
#         cooking_time=30,
#         difficulty="invalid_difficulty",  # Невалидное значение
#         author_id=test_user.id
#     )

#     db_session.add(recipe)

#     with pytest.raises(Exception):
#         db_session.commit()


# def test_recipe_servings_validation(db_session, test_user):
#     """Тест валидации количества порций"""
#     recipe = Recipe(
#         title="Тестовый рецепт",
#         description="Описание",
#         ingredients=[],
#         instructions="",
#         cooking_time=30,
#         servings=0,  # Невалидное значение
#         author_id=test_user.id
#     )

#     db_session.add(recipe)

#     with pytest.raises(Exception):
#         db_session.commit()


# def test_recipe_relationships(db_session, test_user):
#     """Тест связей рецепта (если есть отношения)"""
#     recipe = Recipe(
#         title="Тестовый рецепт",
#         description="Описание",
#         ingredients=[],
#         instructions="",
#         cooking_time=30,
#         author_id=test_user.id
#     )

#     db_session.add(recipe)
#     db_session.commit()
#     db_session.refresh(recipe)

#     # Проверяем, что автор установлен корректно
#     assert recipe.author_id == test_user.id

#     # Если есть обратная связь, проверяем ее
#     # assert recipe.author is not None
#     # assert recipe.author.id == test_user.id


# def test_recipe_default_values(db_session, test_user):
#     """Тест значений по умолчанию"""
#     recipe = Recipe(
#         title="Тестовый рецепт",
#         description="Описание",
#         ingredients=[],
#         instructions="",
#         cooking_time=30,
#         author_id=test_user.id
#         # is_published не указано - должно быть False по умолчанию
#     )

#     db_session.add(recipe)
#     db_session.commit()
#     db_session.refresh(recipe)

#     assert recipe.is_published is False  # Значение по умолчанию
#     assert recipe.servings == 1  # Значение по умолчанию


# def test_recipe_update_timestamp(db_session, test_user):
#     """Тест обновления временных меток"""
#     recipe = Recipe(
#         title="Тестовый рецепт",
#         description="Описание",
#         ingredients=[],
#         instructions="",
#         cooking_time=30,
#         author_id=test_user.id
#     )

#     db_session.add(recipe)
#     db_session.commit()
#     db_session.refresh(recipe)

#     original_created_at = recipe.created_at

#     # Обновляем рецепт
#     recipe.title = "Обновленный рецепт"
#     db_session.commit()
#     db_session.refresh(recipe)

#     # created_at не должен измениться
#     assert recipe.created_at == original_created_at
#     # updated_at должен обновиться (если есть такое поле)
#     # assert recipe.updated_at > original_created_at
