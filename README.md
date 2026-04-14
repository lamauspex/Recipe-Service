# Recipe API

> REST API для платформы рецептов с аутентификацией и поиском

![FastAPI](https://img.shields.io/badge/FastAPI-0.121-blue?style=flat&logo=fastapi)
![Go](https://img.shields.io/badge/Go-1.23-00ADD8?style=flat&logo=go)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat&logo=postgresql)
![MeiliSearch](https://img.shields.io/badge/MeiliSearch-1.11-black?style=flat&logo=meilisearch)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.12-FF6600?style=flat&logo=rabbitmq)
![gRPC](https://img.shields.io/badge/gRPC-1.70-72B4F2?style=flat&logo=grpc)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat&logo=docker)

## 🟢 Технологический стек

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| API (User/Recipe) | FastAPI | HTTP-сервер |
| API (Search) | Go + gRPC | Высокопроизводительный поиск |
| События | RabbitMQ (aio-pika) | Асинхронные события |
| Связь | gRPC | Для общения сервисов |
| База данных | PostgreSQL (x2) | Хранение данных (user, recipe) |
| Поиск | MeiliSearch | Полнотекстовый поиск и автодополнение |
| ORM | SQLAlchemy 2.0 | Работа с БД |
| Миграции | Alembic | Управление схемой БД |
| Валидация | Pydantic v2 | Валидация данных |
| Аутентификация | JWT | Безопасный вход |
| Хеширование | Argon2 | Хеширование паролей|
| DI | Dependency Injector | Внедрение зависимостей |
| Логирование | structlog | Структурированные логи |


## 🟢 Возможности

- Регистрация пользователей
- Аутентификация по JWT
- Создание рецептов
- **Полнотекстовый поиск рецептов** (MeiliSearch)
- **Автодополнение (suggestions)** по названию, ингредиентам, тегам
- Фильтрация по кухне, времени приготовления, сложности
- Пагинация и ранжирование результатов
- Защищённые эндпоинты
- Асинхронная индексация через RabbitMQ
- Структурированное логирование
- Docker-развёртывание

## 🟢 Endpoints

### User Service (REST API) — `localhost:8000`

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/auth/register` | Регистрация пользователя |
| `POST` | `/auth/login` | Вход в систему |

### Recipe Service (REST API) — `localhost:8001`

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/recipes/` | Список рецептов |
| `POST` | `/recipes/` | Создание рецепта |
| `GET` | `/recipes/{id}/` | Рецепт по ID |
| `GET` | `/recipes/search/` | Поиск рецептов |

### Search Service (gRPC) — `localhost:8002`

| Метод | Описание |
|-------|----------|
| `SearchRecipes` | Поиск с фильтрами |
| `GetRecipe` | Получить рецепт по ID |
| `GetSuggestions` | Автодополнение |
| `Health` | Health check |



## 🟢 Архитектура

```
┌──────────────────────────────────────────────────────────────┐
│                     Microservices                            │
├──────────────────┬──────────────────┬───────────────────────┤
│  User Service    │  Recipe Service  │  Search Service       │
│  (FastAPI/Python)│  (FastAPI/Python)│  (Go/gRPC)            │
│  Port: 8000      │  Port: 8001      │  Port: 8002           │
├──────────────────┴──────────────────┴───────────────────────┤
│  PostgreSQL  │  PostgreSQL  │  MeiliSearch  │  RabbitMQ     │
└──────────────────────────────────────────────────────────────┘
```

**User Service:**
- **API** — роутеры и эндпоинты
- **Service** — бизнес-логика (auth, register)
- **Repository** — работа с БД
- **Schemas** — валидация и сериализация

**Recipe Service:**
- **API** — CRUD рецептов, поиск
- **Service** — бизнес-логика
- **Repository** — работа с БД
- **Schemas** — валидация и сериализация

**Search Service:**
- **gRPC API** — SearchRecipes, GetRecipe, GetSuggestions
- **Consumer** — RabbitMQ слушатель событий
- **Repository** — MeiliSearch индекс
- **Config** — управление настройками

## 🟢 Запуск

```bash
git clone https://github.com/lamauspex/recipes.git
```
```bash
# Сборка 
docker compose -f docker/compose.yaml build --no-cache
```
```bash

# Запуск
docker compose -f docker/compose.yaml up -d
```



## 🟢 Документация

После запуска доступна по адресам:

```
http://localhost:8000/docs        # Swagger (User Service)
http://localhost:8000/redoc       # ReDoc (User Service)
http://localhost:8001/docs        # Swagger (Recipe Service)
http://localhost:8001/redoc       # ReDoc (Recipe Service)
```

**Search Service** — gRPC интерфейс, документация в `backend/shared/proto/search_service.proto`

**RabbitMQ Management:** `http://localhost:15672` (admin/rabbitmq-password)

**MeiliSearch Dashboard:** `http://localhost:7700`

---

**Автор**: Резник Кирилл  
**Email**: lamauspex@yandex.ru  
**Telegram**: @lamauspex  
**GitHub**: https://github.com/lamauspex

