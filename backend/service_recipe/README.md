# Recipe Service

> Микросервис для управления рецептами и ингредиентами

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121-blue?style=flat&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat&logo=postgresql)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-ERlang-red?style=flat&logo=rabbitmq)

## Назначение

Сервис отвечает за:
- Создание рецептов
- Управление ингредиентами
- Валидацию данных рецептов
- Публикацию событий в RabbitMQ

## Архитектура

```
Recipe Service
├── api/              # HTTP эндпоинты
│   └── create_recipe.py  # Создание рецептов
├── service/          # Бизнес-логика
│   ├── recipe_service.py # Логика рецептов
│   └── mappers.py        # Преобразование данных
├── repositories/     # Работа с БД
├── schemas/          # Pydantic модели
│   ├── recipe_request.py
│   ├── recipe_response.py
│   └── ingredient_schema.py
├── models/           # SQLAlchemy модели
│   ├── recipe.py
│   └── ingredient.py
├── infrastructure/   # DI, gRPC, RabbitMQ
└── config/           # Конфигурация
```

## Технологии

| Компонент | Технология |
|-----------|------------|
| API | FastAPI |
| База данных | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Миграции | Alembic |
| Валидация | Pydantic v2 |
| События | RabbitMQ (aio-pika) |
| DI | Dependency Injector |

## Эндпоинты

### Создание рецепта

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/v1/recipe/recipes/` | Создание нового рецепта |

**Требования:** Требуется JWT токен в заголовке `Authorization: Bearer <token>`

**Request:**
```json
{
    "name_recipe": "Борщ украинский",
    "description": "Традиционный украинский борщ со сметаной",
    "ingredients": [
        {
            "ingredient": "Свекла",
            "quantity": "300",
            "unit": "г"
        },
        {
            "ingredient": "Капуста",
            "quantity": "200",
            "unit": "г"
        }
    ]
}
```

**Response:**
```json
{
    "id": "uuid",
    "name_recipe": "Борщ украинский",
    "description": "Традиционный украинский борщ со сметаной",
    "ingredients": [
        {
            "id": "uuid",
            "ingredient": "Свекла",
            "quantity": "300",
            "unit": "г"
        }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": null
}
```

## Валидация

### Название рецепта (TitleValidator)
- Минимальная длина: 2 символа
- Максимальная длина: 150 символов
- Допустимые символы: буквы, цифры, дефис, подчёркивание, пробел

### Описание (DescriptionValidator)
- Минимальная длина: 10 символов
- Максимальная длина: 500 символов
- Допустимые символы: буквы, цифры, дефис, подчёркивание, пробел

### Ингредиенты
- Название: обязательно, макс. 50 символов
- Количество: обязательно, макс. 50 символов
- Единица измерения: опционально

## RabbitMQ Events

При создании рецепта публикуется событие:

```json
{
    "user_id": "uuid",
    "recipe_name": "Борщ украинский",
    "event": "recipe_created"
}
```

**Exchange:** `recipe_events`  
**Routing Key:** `recipe.created`

## Взаимодействие с другими сервисами

### User Service (gRPC)
Сервис использует gRPC для валидации JWT токенов:
- `UserServiceClient.validate_token()` — проверка токена
- Получение `user_id` и `email` из токена

### Message Broker (RabbitMQ)
Публикация событий о созданных рецептах для:
- Уведомлений
- Аналитики
- Синхронизации данных



## Тесты

```bash
# Все тесты сервиса
pytest tests/tests_service_recipe/ -v

# Юнит-тесты валидаторов
pytest tests/tests_service_recipe/test_unit.py -v

# Тесты сервисного слоя
pytest tests/tests_service_recipe/test_services.py -v

# Интеграционные тесты
pytest tests/tests_service_recipe/test_integration.py -v
```

### Покрытие тестами

| Файл | Что тестируется |
|------|-----------------|
| `test_unit.py` | TitleValidator, DescriptionValidator |
| `test_services.py` | RecipeService, создание рецептов |
| `test_integration.py` | HTTP эндпоинты, авторизация |

---

**Связь с другими сервисами:**
- User Service → gRPC валидация токенов
- RabbitMQ → публикация событий о рецептах
