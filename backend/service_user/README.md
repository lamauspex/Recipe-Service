# User Service

> Микросервис для управления пользователями и аутентификацией

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121-blue?style=flat&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat&logo=postgresql)

## Назначение

Сервис отвечает за:
- Регистрацию новых пользователей
- Аутентификацию (вход в систему)
- Управление JWT токенами
- Выход из системы (инвалидация токенов)

## Архитектура

```
User Service
├── api/              # HTTP эндпоинты
│   ├── auth_user.py      # Аутентификация
│   └── register_user.py  # Регистрация
├── service/          # Бизнес-логика
├── repositories/     # Работа с БД
├── schemas/          # Pydantic модели
├── models/           # SQLAlchemy модели
├── infrastructure/   # DI, gRPC клиенты
└── middleware/       # Обработка ошибок
```

## Технологии

| Компонент | Технология |
|-----------|------------|
| API | FastAPI |
| База данных | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Аутентификация | JWT (access + refresh) |
| Хеширование | Argon2 |
| Валидация | Pydantic v2 |
| DI | Dependency Injector |

## Эндпоинты

### Регистрация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/v1/auth/register` | Регистрация нового пользователя |

**Request:**
```json
{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "Иван Иванов"
}
```

**Response:**
```json
{
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Иван Иванов",
    "created_at": "2024-01-01T00:00:00Z"
}
```

### Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/v1/auth/login` | Вход в систему |

**Request:**
```json
{
    "email": "user@example.com",
    "password": "securepassword"
}
```

**Response:**
```json
{
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
}
```

### Обновление токена

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/v1/auth/refresh` | Обновление access токена |

**Request:**
```json
{
    "refresh_token": "eyJ..."
}
```

### Выход

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/v1/auth/logout` | Выход из системы |

**Request:**
```json
{
    "refresh_token": "eyJ..."
}
```

## JWT Токены

Сервис использует two-token схему:

1. **Access Token** — короткоживущий токен (15 минут)
   - Используется для авторизации запросов
   - Передаётся в заголовке `Authorization: Bearer <token>`

2. **Refresh Token** — долгоживущий токен (7 дней)
   - Используется для обновления access токена
   - Хранится в БД для возможности инвалидации


## Зависимости

Сервис предоставляет gRPC интерфейс для других сервисов:
- `UserServiceClient` — валидация токенов
- Проверка аутентификации через `get_current_user`

## Тесты

```bash
# Все тесты сервиса
pytest tests/tests_users_service/ -v

# Только юнит-тесты
pytest tests/tests_users_service/test_unit.py -v

# Только интеграционные
pytest tests/tests_users_service/test_integration.py -v
```

---

**Связь с другими сервисами:**
- Recipe Service использует gRPC для валидации JWT токенов
- Взаимодействие через `UserServiceClient`
