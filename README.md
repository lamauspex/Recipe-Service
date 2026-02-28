# Recipe API

> REST API для платформы рецептов с аутентификацией и поиском

![FastAPI](https://img.shields.io/badge/FastAPI-0.121-blue?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat&logo=postgresql)
![JWT](https://img.shields.io/badge/JWT-Auth-orange)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat&logo=docker)

## 🟢 Технологический стек

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| API | FastAPI | HTTP-сервер |
| База данных | PostgreSQL | Хранение данных |
| ORM | SQLAlchemy 2.0 | Работа с БД |
| Миграции | Alembic | Управление схемой БД |
| Валидация | Pydantic v2 | Валидация данных |
| Аутентификация | JWT + Argon2 | Безопасный вход |
| DI | dependency-injector | Внедрение зависимостей |
| Логирование | structlog | Структурированные логи |

## 🟢 Ключевые навыки

- **FastAPI** — асинхронный REST API
- **Clean Architecture** — сервисная архитектура
- **PostgreSQL** — реляционная база данных
- **JWT-аутентификация** — безопасность
- **Alembic** — миграции базы данных
- **Dependency Injection** — управление зависимостями
- **Структурированное логирование** — мониторинг
- **Docker** — контейнеризация

## 🟢 Возможности

- Регистрация пользователей
- Аутентификация по JWT
- Создание рецептов
- Поиск рецептов
- Пагинация и фильтрация
- Защищённые эндпоинты
- Структурированное логирование
- Docker-развёртывание

## 🟢 Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/auth/register` | Регистрация пользователя |
| `POST` | `/auth/login` | Вход в систему |
| `GET` | `/recipes/` | Список рецептов |
| `POST` | `/recipes/` | Создание рецепта |
| `GET` | `/recipes/{id}/` | Рецепт по ID |
| `GET` | `/recipes/search/` | Поиск рецептов |



## 🟢 Архитектура

```
┌─────────────────────────────────────────────┐
│                  FastAPI                     │
├─────────────────────────────────────────────┤
│  service_user  │  service_recipe  │  ...    │
├─────────────────────────────────────────────┤
│            SQLAlchemy + PostgreSQL           │
└─────────────────────────────────────────────┘
```

Каждый сервис содержит:
- **API** — роутеры и эндпоинты
- **Service** — бизнес-логика
- **Repository** — работа с БД
- **Schemas** — валидация и сериализация

## 🟢 Локальный запуск

```bash
# Клонирование
git clone https://github.com/lamauspex/recipes.git
cd recipes

# Установка зависимостей
pip install -r requirements.txt

# Запуск
python main.py
```

## 🟢 Запуск в Docker

```bash
docker-compose up -d
```

## 🟢 Документация

После запуска доступна по адресам:

```
http://localhost:8000/docs        # Swagger
http://localhost:8000/redoc       # ReDoc
```

---

**Автор**: Резник Кирилл  
**Email**: lamauspex@yandex.ru  
**Telegram**: @lamauspex  
**GitHub**: https://github.com/lamauspex
