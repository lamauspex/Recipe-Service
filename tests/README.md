# =========== Тесты =========== 

## 🚀 Быстрый старт (локальный запуск)

### 1. Установка зависимостей

```bash
# В корне проекта
pip install -r requirements-test.txt
```


### 2. Запуск тестов

```bash
# Из корневого каталога проекта
cd /path/to/R_M

# Все тесты
pytest

# Конкретный сервис
pytest tests/tests_service_recipe/
pytest tests/tests_users_service/

# Конкретный файл
pytest tests/tests_service_recipe/test_services.py

# С покрытием кода
pytest --cov=backend --cov-report=html

# Тесты с подробным выводом
pytest -v
```

---

## 📋 gRPC тесты

Для тестов gRPC требуется запущенный gRPC сервер:

```bash
# Терминал 1: Запуск gRPC сервера user_service
cd /path/to/R_M
python -m backend.service_user.src.infrastructure.grpc_server

# Терминал 2: Запуск тестов клиента
python -m tests.tests_grpc_server.client

# Терминал 3: Интеграционные тесты
python -m tests.tests_grpc_server.integration_test
```

---

## 🐳 Запуск с Docker (интеграционные тесты)

Для тестов, требующих реальных БД и RabbitMQ:

```bash
# Запустить инфраструктуру
cd docker
docker compose -f compose_infra.yml up -d

# Запустить тесты
pytest tests/

# Остановить инфраструктуру
docker compose -f compose_infra.yml down
```

---

## 🔧 Требования

### Минимальные требования:
- Python 3.12+
- pip

### Опционально (для интеграционных тестов):
- Docker & Docker Compose
- PostgreSQL
- RabbitMQ

### Переменные окружения:
- `.env.test` — тестовая конфигурация (в папке `tests/`)
- `TESTING=true` — включает тестовый режим




# =========== Postman =========== 

## Импорт

`User Service.postman_collection.json` → Import → выбрать файл

## Переменные окружения

`base_url`: `http://localhost:8000` (user) / `http://localhost:8001` (recipe)

## Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/auth/register` | Регистрация |
| POST | `/api/v1/auth/login` | Логин |
| POST | `/api/v1/auth/refresh` | Обновить токен |
| POST | `/api/v1/auth/logout` | Выйти |