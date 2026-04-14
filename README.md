# 🍳 Платформа Recipe API

> **Микросервисная платформа для поиска рецептов с низкой задержкой и высокой масштабируемостью.**

> Построена на принципах *CQRS*, *Event‑Driven Architecture* и *Clean Architecture*.
> Оптимизирована для производительности: поиск < 50 ms (p95), индексация < 200 ms.
---

![Go](https://img.shields.io/badge/Go-1.23-00ADD8?style=flat&logo=go)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121-blue?style=flat&logo=fastapi)
![MeiliSearch](https://img.shields.io/badge/MeiliSearch-1.11-black?style=flat&logo=meilisearch)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.12-FF6600?style=flat&logo=rabbitmq)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat&logo=postgresql)
![gRPC](https://img.shields.io/badge/gRPC-1.70-72B4F2?style=flat&logo=grpc)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Ключевые архитектурные решения

* **CQRS**: раздельные модели чтения (MeiliSearch) и записи (PostgreSQL) для оптимальной производительности.
* **Event‑Driven**: асинхронная индексация через RabbitMQ — новые рецепты появляются в поиске за < 200 ms.
* **gRPC**: типобезопасное взаимодействие между сервисами (Search Service на Go, остальные — на Python).
* **Разделение ответственности**: User Service, Recipe Service и Search Service развёртываются и масштабируются независимо.
* **Безопасность**: JWT‑аутентификация, хеширование паролей Argon2, CORS.

## Компоненты

| Сервис | Порт | Технология | Назначение | Документация |
|------|------|----------|-----------|-------------|
| User Service | `:8000` | FastAPI (Python) | Аутентификация (JWT), регистрация, управление профилем | [README](backend/service_user/README.md) |
| Recipe Service | `:8001` | FastAPI (Python) | CRUD рецептов, управление ингредиентами, публикация | [README](backend/service_recipe/README.md) |
| Search Service | `:8002` | Go + gRPC | Высокопроизводительный поиск, автодополнение, ранжирование | [README](backend/service_search/README.md) |

## Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (порты 8000-8002)            │
├───────────────┬───────────────┬─────────────────────────────┤
│ User Service  │ Recipe Service│ Search Service (Go)         │
│  FastAPI      │  FastAPI      │  gRPC + MeiliSearch         │
├───────────────┴───────────────┴─────────────────────────────┤
│  PostgreSQL  │  PostgreSQL  │  MeiliSearch  │  RabbitMQ     │
│  (Пользов.)  │  (Рецепты)   │  (Поиск)      │  (События)    │
└─────────────────────────────────────────────────────────────┘
```

## Производительность (тестовые нагрузки)

* Задержка поиска: **< 50 ms** (p95).
* Время ответа API: **< 100 ms** (p95).
* Поддерживаемая нагрузка: **1 000+** одновременных пользователей.

## Быстрый старт
### Клон
```bash
git clone https://github.com/lamauspex/recipes.git
```
### Сборка 
```bash
docker compose -f docker/compose.yaml build --no-cache
```
### Запуск
```bash
docker compose -f docker/compose.yaml up -d
```


**Автор**: Резник Кирилл  
**Email**: lamauspex@yandex.ru  
**Telegram**: @lamauspex  
**GitHub**: https://github.com/lamauspex