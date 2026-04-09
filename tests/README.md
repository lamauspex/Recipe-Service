# =========== Тесты =========== 

## Запуск

```bash
# Все тесты
pytest

# Конкретный сервис
pytest tests/service_user/
pytest tests/service_recipe/
```




# =========== gRPC тесты  =========== 

```bash
# Терминал 1: сервер
python -m backend.service_user.src.infrastructure.grpc_server

# Терминал 2: клиент
python -m tests.tests_grpc_server.client

# Терминал 3: интеграционные тесты
python -m tests.tests_grpc_server.integration_test
```

## Требования

- Запущенные БД и RabbitMQ (см. `docker/compose.infra.yml`)
- Переменные окружения в `.env`




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