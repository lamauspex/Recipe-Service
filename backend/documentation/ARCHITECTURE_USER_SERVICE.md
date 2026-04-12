# Архитектура User Service

**Статус:** ✅ Production Ready  
**Версия:** 1.0.0  
**Последнее обновление:** 2026-04-10

---

## 📋 Оглавление

1. [Обзор](#обзор)
2. [Принципы архитектуры](#принципы-архитектуры)
3. [Структура сервиса](#структура-сервиса)
4. [Процесс запуска](#процесс-запуска)
5. [Интеграция gRPC](#интеграция-grpc)
6. [Слой базы данных](#слой-базы-данных)
7. [Дизайн API](#дизайн-api)
8. [Безопасность](#безопасность)
9. [Деплой](#деплой)
10. [Мониторинг и проверки здоровья](#мониторинг--проверки-здоровья)
11. [Устранение неполадок](#устранение-неполадок)

---

## Обзор

User Service — это **микросервис**, предоставляющий функциональность управления пользователями и аутентификации. Он предоставляет **как REST API (FastAPI)**, так и **gRPC** интерфейсы для максимальной гибкости в межсервисном взаимодействии.

### Ключевые возможности

- **Регистрация и аутентификация пользователей** - JWT-аутентификация с refresh токенами
- **Управление паролями** - Безопасное хеширование паролей (Argon2/bcrypt)
- **Подтверждение email** - Токенизированное подтверждение email
- **Восстановление аккаунта** - Сброс пароля
- **Ограничение частоты запросов** - Защита от DDoS и злоупотреблений
- **Блокировка аккаунта** - Защита от brute force атак
- **Контроль доступа на основе ролей** - Роли и разрешения пользователей
- **Межсервисное взаимодействие через gRPC** - Эффективные внутренние API вызовы

---

## Принципы архитектуры

### Паттерны проектирования

| Паттерн | Использование | Обоснование |
|---------|---------------|-------------|
| **Dependency Injection** | `dependency-injector` контейнер | Тестируемость, слабая связанность |
| **Repository Pattern** | SQL репозитории с протоколами | Абстракция БД, тестируемость |
| **Service Layer** | Бизнес-логика в сервисах | Разделение ответственности |
| **DTO Pattern** | Pydantic схемы для ввода/вывода | Валидация, сериализация |
| **Middleware Pattern** | Стек middleware FastAPI | Кросс-функциональные задачи |
| **Graceful Shutdown** | Обработчики сигналов + finally блоки | Корректная очистка ресурсов |

### Архитектурные слои

```
┌─────────────────────────────────────────────────┐
│                API Layer                        │
│  FastAPI Routers (auth, register, health)      │
├─────────────────────────────────────────────────┤
│              Service Layer                      │
│  AuthService, RegisterService (бизнес-логика)  │
├─────────────────────────────────────────────────┤
│            Repository Layer                     │
│  SQLUserRepository, SQLTokenRepository         │
├─────────────────────────────────────────────────┤
│             Core Layer                          │
│  JWTService, PasswordService, Validators       │
├─────────────────────────────────────────────────┤
│           Infrastructure Layer                  │
│  gRPC, Database, DI Container, Config          │
└─────────────────────────────────────────────────┘
```

---

## Структура сервиса

### Расположение директорий

```
backend/service_user/
├── main.py                          # Точка входа (3 строки)
├── src/
│   ├── app_users.py                 # Factory для создания FastAPI app
│   ├── runner.py                    # Оркестрация сервиса (ServiceRunner)
│   ├── lifespan.py                  # Управление жизненным циклом (миграции, БД)
│   │
│   ├── api/                         # REST API endpoints
│   │   ├── __init__.py             # Экспорт api_router
│   │   ├── auth_user.py            # /auth_users/* endpoints
│   │   ├── register_user.py        # /register_users/* endpoints
│   │   └── health.py               # /health endpoint
│   │
│   ├── config/                      # Управление конфигурацией
│   │   ├── config_api.py           # Настройки API
│   │   ├── config_auth.py          # Настройки Auth/JWT
│   │   ├── config_cors.py          # Настройки CORS
│   │   ├── config_grpc.py          # Настройки gRPC
│   │   └── ...
│   │
│   ├── core/                        # Ядро бизнес-логики
│   │   ├── service_jwt.py          # Управление JWT токенами
│   │   ├── service_password.py     # Хеширование/проверка паролей
│   │   ├── validator_auth.py       # Валидаторы аутентификации
│   │   └── validator_name.py       # Уникальность имени пользователя
│   │
│   ├── infrastructure/              # Инфраструктурные задачи
│   │   ├── container.py            # DI Контейнер (dependency-injector)
│   │   ├── dependencies.py         # FastAPI Depends
│   │   └── grpc/                   # Реализация gRPC
│   │       ├── server.py           # UserServiceServicer
│   │       ├── runner.py           # GrpcRunner (запуск/остановка)
│   │       └── __init__.py         # Экспорт модуля
│   │
│   ├── models/                      # SQLAlchemy модели
│   │   ├── user.py                 # Модель User
│   │   ├── token.py                # Модель RefreshToken
│   │   └── login_attempt.py        # Модель LoginAttempt
│   │
│   ├── protocols/                   # Интерфейсы репозиториев
│   │   ├── user_repository.py      # UserRepositoryProtocol
│   │   └── token_repository.py     # TokenRepositoryProtocol
│   │
│   ├── repositories/                # Реализации репозиториев
│   │   ├── sql_user_repository.py  # SQLUserRepository
│   │   └── sql_token_repository.py # SQLTokenRepository
│   │
│   ├── schemas/                     # Pydantic DTO
│   │   ├── auth/                   # Схемы запросов/ответов для auth
│   │   ├── register/               # Схемы запросов/ответов для регистрации
│   │   └── base/                   # Базовые утилиты схем
│   │
│   ├── service/                     # Бизнес-сервисы
│   │   ├── auth_service/           # Реализация AuthService
│   │   └── register_service/       # Реализация RegisterService
│   │
│   ├── middleware/                  # FastAPI middleware
│   │   └── exception_middleware.py # Обработка исключений
│   │
│   └── exception/                   # Кастомные исключения
│       ├── base.py                 # Базовые классы исключений
│       └── auth.py                 # Auth-специфичные исключения
│
├── migration/                       # Alembic миграции
│   └── migrations/
│       └── versions/
│
├── requirements.txt                 # Python зависимости
├── Dockerfile                       # Определение контейнера
└── .env                             # Переменные окружения
```

---

## Процесс запуска

### Последовательность запуска FastAPI

```
main.py
  ↓
ServiceRunner.run()
  ├─→ container.api_config()      # Загрузка конфигурации API
  ├─→ container.grpc_config()     # Загрузка конфигурации gRPC
  │
  ├─→ create_app()                # Factory для создания FastAPI app
  │   └─→ lifespan контекст
  │       ├─→ Alembic миграции    # database.upgrade("head")
  │       ├─→ Тест подключения БД # connection_manager.test_connection()
  │       └─→ Настройка логирования # structlog конфигурация
  │
  ├─→ GrpcRunner.run_in_background()
  │   └─→ threading.Thread
  │       └─→ GrpcRunner.run()
  │           ├─→ Создание gRPC сервера
  │           ├─→ Добавление UserServiceServicer
  │           ├─→ Добавление HealthServicer
  │           └─→ server.start()
  │
  └─→ uvicorn.run()               # Запуск FastAPI
      └─→ await lifespan.aclose() # Graceful shutdown
          └─→ ServiceRunner._shutdown()
              └─→ grpc_runner.stop()
```

### Таймлайн запуска

| Время | Событие |
|-------|---------|
| T+0s | Запуск контейнера |
| T+1s | Импорт Python (main.py → runner.py) |
| T+2s | Вызов ServiceRunner.run() |
| T+3s | Создание FastAPI app, запуск lifespan |
| T+4s | Выполнение Alembic миграций |
| T+5s | Тест подключения к БД |
| T+6s | Запуск gRPC сервера (фоновый поток) |
| T+7s | Запуск FastAPI (uvicorn) |
| T+8s | **Сервис готов** (оба API работают) |

---

## Интеграция gRPC

### Архитектурное решение

**Почему gRPC?**
- **Производительность** - Бинарный протокол (Protobuf) vs JSON
- **Сильная типизация** - Валидация контрактов на этапе компиляции
- **Генерация кода** - Автоматически сгенерированный код клиента/сервера
- **Межсервисное взаимодействие** - Эффективный внутренний API

### Реализация gRPC сервера

**Расположение:** `backend/service_user/src/infrastructure/grpc/`

```python
# server.py - Реализация UserServiceServicer
class UserServiceServicer(user_service_pb2_grpc.UserServiceServicer):
    def ValidateToken(self, request, context):
        # Декодирование JWT, валидация, возврат информации о пользователе
        pass
    
    def GetUserById(self, request, context):
        # Запрос к базе данных, возврат данных пользователя
        pass
```

**Proto определение:** `backend/shared/proto/user_service.proto`

```protobuf
service UserService {
  rpc ValidateToken(ValidateTokenRequest) returns (ValidateTokenResponse);
  rpc GetUserById(GetUserByIdRequest) returns (GetUserByIdResponse);
}
```

### gRPC клиент (другие сервисы)

**Пример:** `backend/service_recipe/src/infrastructure/user_grpc_client.py`

```python
class UserServiceClient:
    async def validate_token(self, token: str) -> dict:
        response = await self._stub.ValidateToken(
            user_service_pb2.ValidateTokenRequest(token=token)
        )
        return {"valid": response.valid, "user_id": response.user_id}
```

### Важные замечания

⚠️ **Ограничение обработчиков сигналов**
- `signal.signal()` **работает только в главном потоке**
- gRPC работает в фоновом потоке → сигналы отключены
- Graceful shutdown обрабатывается через `ServiceRunner._shutdown()`

⚠️ **Потокобезопасность**
- gRPC сервер использует `ThreadPoolExecutor(max_workers=10)`
- Сессии базы данных должны быть thread-local (SQLAlchemy делает это)
- JWT сервис stateless → потокобезопасен

---

## Слой базы данных

### ORM: SQLAlchemy 2.0+

**Модели:**
- `User` - Учётные записи пользователей с ролями, подтверждением email
- `RefreshToken` - JWT refresh токены с отзывом
- `LoginAttempt` - Отслеживание неудачных попыток входа для защиты от brute force

**Пул соединений:**
```python
# config: Размер пула = 10, Max overflow = 20
# Production: Настроить в зависимости от ожидаемой нагрузки
```

### Миграции: Alembic

**Расположение:** `backend/service_user/migration/`

**Автозапуск при старте:**
```python
# lifespan.py
alembic_cfg = Config("backend/service_user/migration/alembic.ini")
command.upgrade(alembic_cfg, "head")
```

**Ручная миграция:**
```bash
# Создать новую миграцию
alembic -c backend/service_user/migration/alembic.ini revision --autogenerate -m "описание"

# Применить миграции
alembic -c backend/service_user/migration/alembic.ini upgrade head

# Откатить
alembic -c backend/service_user/migration/alembic.ini downgrade -1
```

---

## Дизайн API

### REST API endpoints

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| POST | `/api/v1/auth_users/login` | Вход пользователя | Нет |
| POST | `/api/v1/auth_users/refresh` | Обновление access токена | Refresh токен |
| POST | `/api/v1/auth_users/logout` | Выход пользователя | Refresh токен |
| POST | `/api/v1/register_users/register` | Регистрация пользователя | Нет |
| GET | `/health` | Проверка здоровья | Нет |

### Паттерны запроса/ответа

**Запрос входа:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Ответ входа:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Формат ответа об ошибке

```json
{
  "error": {
    "message": "Неверные учетные данные!",
    "code": "INVALID_CREDENTIALS",
    "status_code": 401,
    "timestamp": "2026-04-10T19:36:07.105Z"
  }
}
```

---

## Безопасность

### Конфигурация JWT

| Параметр | Значение | Назначение |
|----------|----------|------------|
| `SECRET_KEY` | Настраивается | Ключ подписи |
| `ALGORITHM` | HS256 | Алгоритм подписи |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 15 | Краткосрочный access токен |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 30 | Долгосрочный refresh токен |
| `JWT_VERIFICATION_TOKEN_EXPIRE_HOURS` | 24 | Подтверждение email |
| `JWT_PASSWORD_RESET_TOKEN_EXPIRE_HOURS` | 1 | Сброс пароля |

### Безопасность паролей

**Алгоритмы:** Argon2-cffi (основной), bcrypt (резервный)

**Требования:**
- Минимальная длина: 8 символов
- Максимальная длина: 128 символов
- Требуются заглавные буквы: Да
- Требуются строчные буквы: Да
- Требуются цифры: Да
- Требуются спецсимволы: Да

### Ограничение частоты запросов

| Лимит | Окно | Действие |
|-------|------|----------|
| 60 запросов | 1 минута | Отслеживание |
| 1000 запросов | 1 час | Отслеживание |
| 5 неудачных входов | 15 минут | Блокировка (30 мин) |

---

## Деплой

### Docker Compose

**Файл:** `docker/compose.app.yml`

```yaml
services:
  service_user:
    build: backend/service_user
    ports:
      - "8000:8000"   # REST API
      - "50051:50051" # gRPC
    depends_on:
      postgres_user:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
```

### Переменные окружения

**Критические переменные:**

```env
# API
USER_SERVICE_HOST=0.0.0.0
USER_SERVICE_PORT=8000

# gRPC
USER_SERVICE_GRPC_ENABLED=true
USER_SERVICE_GRPC_PORT=50051

# База данных
DB_HOST=postgres_user
DB_PORT=5432
DB_NAME=users_db
DB_USER=user_service
DB_PASSWORD=258075

# JWT
USER_SERVICE_SECRET_KEY=your-super-secret-key
USER_SERVICE_ALGORITHM=HS256
```

### Чеклист для production

- [ ] Установить сильный `SECRET_KEY` (32+ случайных символов)
- [ ] Включить HTTPS для REST API
- [ ] Настроить production базу данных (не development)
- [ ] Настроить мониторинг (Prometheus/Grafana)
- [ ] Настроить агрегацию логов (ELK/CloudWatch)
- [ ] Включить security headers (CORS, HSTS)
- [ ] Установить лимиты ресурсов (CPU, память)
- [ ] Настроить авто-скейлинг
- [ ] Настроить стратегию бэкапов
- [ ] Включить аудит логирования

---

## Мониторинг и проверки здоровья

### Эндпоинты здоровья

**REST API:**
```
GET /health
Ответ: {"status": "healthy", "service": "user_service"}
```

**gRPC:**
```proto
service Health {
  rpc Check(HealthCheckRequest) returns (HealthCheckResponse);
}
```

### Метрики

**Prometheus:**
- Порт: `9090` (настраивается через `USER_SERVICE_METRICS_PORT`)
- Путь: `/metrics`

**Ключевые метрики:**
- Количество запросов
- Длительность запросов
- Частота ошибок
- Пул соединений базы данных
- Активные пользователи

---

## Устранение неполадок

### Распространённые проблемы

| Проблема | Симптомы | Решение |
|----------|----------|---------|
| **Файлы proto повреждены** | `SyntaxError: null bytes` | Перегенерировать `*_pb2.py` файлы |
| **Отсутствует google.rpc** | `ModuleNotFoundError: google.rpc` | Добавить `googleapis-common-protos[grpc]` |
| **Обработчики сигналов падают** | `ValueError: signal only works in main thread` | Не использовать `signal.signal()` в потоках |
| **Подключение к БД не удаётся** | `Connection refused` | Проверить `DB_HOST`, `DB_PORT`, сеть |
| **Порт уже используется** | `Address already in use` | Проверить что порты 8000, 50051 не заняты |

### Команды для отладки

```bash
# Проверить логи
docker logs -f service_user

# Проверить порт gRPC
netstat -ano | findstr :50051

# Протестировать REST API
curl http://localhost:8000/health

# Протестировать подключение к БД
docker exec -it postgres_user psql -U user_service -d users_db

# Перегенерировать proto файлы
python -m grpc_tools.protoc \
  -I./backend/shared/proto \
  --python_out=./backend/shared/proto \
  --grpc_python_out=./backend/shared/proto \
  ./backend/shared/proto/user_service.proto
```

### Анализ логов

**Ключевые уровни логирования:**
- `INFO` - Запуск сервиса, успешные операции
- `WARNING` - Некритичные проблемы
- `ERROR` - Ошибки операций
- `DEBUG` - Детальная отладка (установить `DEBUG=True`)

**Формат лога:**
```
2026-04-10 19:36:07 [info] User Service started docs_url=http://...
```

---

## Соображения для Senior-разработчиков

### Оптимизация производительности

1. **Пул соединений** - Настроить `POOL_SIZE` и `MAX_OVERFLOW` в зависимости от нагрузки
2. **gRPC vs REST** - Использовать gRPC для внутренних вызовов (в 10 раз быстрее REST)
3. **Кэширование** - Redis для часто запрашиваемых данных (профили пользователей, конфигурации)
4. **Индексация БД** - Индексировать столбцы `email`, `user_name`, `user_id`
5. **Async/Await** - Использовать async для I/O-bound операций

### Масштабируемость

1. **Горизонтальное масштабирование** - Несколько экземпляров service_user за балансировщиком нагрузки
2. **Репликация БД** - Read replicas для read-heavy нагрузок
3. **Управление сессиями** - Redis для общего состояния сессий (не JWT)
4. **Очередь сообщений** - RabbitMQ для асинхронных задач (email, уведомления)

### Усиление безопасности

1. **Управление секретами** - Использовать HashiCorp Vault или AWS Secrets Manager
2. **Сетевые политики** - Ограничить порт gRPC (50051) только внутренней сетью
3. **Аудит логирования** - Логировать все события аутентификации
4. **Ограничение частоты** - Реализовать лимиты на IP и на пользователя
5. **OWASP соответствие** - Следовать руководству OWASP Top 10

### Стратегия тестирования

1. **Unit Tests** - Тестировать сервисы в изоляции (mock репозитории)
2. **Integration Tests** - Тестировать с реальной БД (test containers)
3. **E2E Tests** - Тестировать полный поток аутентификации
4. **Load Tests** - Тестировать под нагрузкой (k6, Locust)
5. **Security Tests** - OWASP ZAP, SAST/DAST сканирование

---

## Участники

- **Архитектура:** Senior Backend Team
- **Реализация gRPC:** NLP-Core-Team
- **Проверка безопасности:** Security Team
- **Документация:** Senior Backend Team

---

## Changelog

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0.0 | 2026-04-10 | Первый production релиз с поддержкой gRPC |

---

**Владелец документа:** NLP-Core-Team  
**Цикл пересмотра:** Квартально  
**Следующий пересмотр:** 2026-07-10
