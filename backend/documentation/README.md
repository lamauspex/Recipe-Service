# 📚 Документация проекта R_M

Микросервисная система на Python (FastAPI + gRPC) с PostgreSQL и RabbitMQ.

---

## 🚀 Быстрый старт

```bash
# Запуск всех сервисов
docker compose -f docker/compose.yaml up

# Проверка здоровья
curl http://localhost:8000/health  # service_user
curl http://localhost:8001/health  # service_recipe
```

---

## 📑 Навигация

| Раздел | Описание | Для кого |
|--------|----------|----------|
| [01. Getting Started](01-getting-started/) | Установка, конфигурация, быстрый запуск | Все |
| [02. Architecture](02-architecture/) | Архитектура системы, потоки данных | Senior/Middle |
| [03. Development](03-development/) | Настройка среды, создание API, миграции | Разработчики |
| [04. API Reference](04-api/) | Документация API endpoints | Frontend/Consumers |
| [05. Deployment](05-deployment/) | Docker, production, мониторинг | DevOps |
| [06. Troubleshooting](06-troubleshooting/) | Типичные проблемы и решения | Все |
| [07. Appendix](07-appendix/) | Термины, соглашения, conventions | Для справки |

---

## 🏗️ Архитектура вкратце

```
┌─────────────────┐     ┌─────────────────┐
│  service_user   │     │ service_recipe  │
│  (FastAPI+gRPC) │     │  (FastAPI only) │
│  Port: 8000     │     │  Port: 8001     │
│  gRPC: 50051    │     │                 │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │    gRPC (50051)       │
         └───────────────────────┘
                   ↓
         ┌─────────────────┐
         │    RabbitMQ     │
         │  Port: 5672     │
         └─────────────────┘
                   ↓
    ┌──────────────┴───────────────┐
    │                              │
┌───▼─────┐                  ┌─────▼────┐
│postgres │                  │ postgres │
│ _user   │                  │ _recipe  │
│5434:5432│                  │5435:5432 │
└─────────┘                  └──────────┘
```

---

## 🛠️ Стек технологий

| Компонент | Технологии |
|-----------|------------|
| **Web Framework** | FastAPI, Uvicorn |
| **Database** | PostgreSQL 15, SQLAlchemy, Alembic |
| **Message Broker** | RabbitMQ 3.13 |
| **RPC** | gRPC (protobuf) |
| **DI Container** | dependency-injector |
| **Config** | Pydantic Settings |
| **Logging** | structlog |
| **Auth** | JWT (PyJWT) |
| **Deployment** | Docker, Docker Compose |

---

## 📂 Структура проекта

```
backend/
├── service_user/          # User Service (FastAPI + gRPC)
│   ├── src/
│   │   ├── api/           # API endpoints
│   │   ├── models/        # SQLAlchemy models
│   │   ├── repositories/  # Data access layer
│   │   ├── service/       # Business logic
│   │   ├── config/        # Configuration classes
│   │   └── infrastructure/ # DI container, dependencies
│   └── Dockerfile
├── service_recipe/        # Recipe Service (FastAPI only)
│   ├── src/
│   │   ├── api/           # API endpoints
│   │   ├── models/        # SQLAlchemy models
│   │   ├── repositories/  # Data access layer
│   │   ├── service/       # Business logic
│   │   ├── config/        # Configuration classes
│   │   └── infrastructure/ # DI container, dependencies
│   └── Dockerfile
├── shared/                # Общие модули
│   ├── proto/             # gRPC protobuf definitions
│   ├── database/          # Database configs, connection
│   └── logging/           # Logging setup, middleware
└── documentation/         # Эта документация

docker/
├── compose.yaml           # Главный compose (включает infra + app)
├── compose.infra.yml      # PostgreSQL, RabbitMQ
└── compose.app.yml        # service_user, service_recipe
```

---

## 📊 Порты

| Сервис | HTTP | gRPC | PostgreSQL | RabbitMQ |
|--------|------|------|------------|----------|
| **service_user** | 8000 | 50051 | 5434:5432 | - |
| **service_recipe** | 8001 | - | 5435:5432 | - |
| **RabbitMQ** | - | - | - | 5672:5672 |
| **RabbitMQ Management** | - | - | - | 15672:15672 |

---

## ⚡ Команды

```bash
# Запуск всех сервисов
docker compose -f docker/compose.yaml up

# Запуск отдельных сервисов
docker compose -f docker/compose.yaml up service_user
docker compose -f docker/compose.yaml up service_recipe

# Пересборка с кэшем
docker compose -f docker/compose.yaml build

# Пересборка без кэша
docker compose -f docker/compose.yaml build --no-cache

# Просмотр логов
docker logs service_user
docker logs service_recipe

# Остановка
docker compose -f docker/compose.yaml down

# Остановка и очистка volumes
docker compose -f docker/compose.yaml down -v
```

---

## 📝 Чеклист для нового разработчика

- [ ] Установить Docker Desktop
- [ ] Клонировать репозиторий
- [ ] Запустить `docker compose up`
- [ ] Проверить `/health` endpoints
- [ ] Открыть API docs: http://localhost:8000/docs, http://localhost:8001/docs
- [ ] Открыть RabbitMQ Management: http://localhost:15672 (admin/rabbitmq-password)

---

## 🆘 Поддержка

При проблемах смотри [Troubleshooting](06-troubleshooting/common-issues.md).
