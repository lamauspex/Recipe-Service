
"""
Интеграционные тесты для API рецептов
"""


def test_create_recipe_success(client, auth_headers):
    """Тест успешного создания рецепта через API"""
    recipe_data = {
        "title": "Новый рецепт",
        "description": "Описание нового рецепта",
        "ingredients": ["ингредиент 1", "ингредиент 2"],
        "instructions": ["Шаг 1", "Шаг 2"],
        "cooking_time": 30,
        "difficulty": "легко",
        "servings": 2
    }

    response = client.post(
        "/api/recipes/",
        json=recipe_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Новый рецепт"
    assert "id" in data


def test_get_recipes_list(client):
    """Тест получения списка рецептов"""
    response = client.get("/api/recipes/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_recipe_by_id(client, test_recipe):
    """Тест получения рецепта по ID"""
    response = client.get(f"/api/recipes/{test_recipe.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_recipe.id)
    assert data["title"] == test_recipe.title
