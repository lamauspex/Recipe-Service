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
| События | RabbitMQ (aio-pika) | Асинхронные события |
| Связь | gRPC | Для общения сервисов |
| База данных | PostgreSQL | Хранение данных |
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
│                  FastAPI                    │
├─────────────────────────────────────────────┤
│  service_user  │  service_recipe  │  ...    │
├─────────────────────────────────────────────┤
│            SQLAlchemy + PostgreSQL          │
└─────────────────────────────────────────────┘
```

Каждый сервис содержит:
- **API** — роутеры и эндпоинты
- **Service** — бизнес-логика
- **Repository** — работа с БД
- **Schemas** — валидация и сериализация

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
http://localhost:8000/docs        # Swagger
http://localhost:8000/redoc       # ReDoc
```

---

**Автор**: Резник Кирилл  
**Email**: lamauspex@yandex.ru  
**Telegram**: @lamauspex  
**GitHub**: https://github.com/lamauspex

