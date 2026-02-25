# Database Service

Микросервис для управления подключением к базе данных и миграциями. Предоставляет единый интерфейс для работы с SQLAlchemy через DI контейнер.

## Назначение

- Управление соединениями с базой данных (PostgreSQL/SQLite для тестов)
- Провайдер сессий для FastAPI через dependency injection
- Запуск миграций Alembic
- Graceful shutdown соединений

## Установка

### Требования

- Python 3.11+
- PostgreSQL (для production)
- SQLite (для тестирования, встроен)

### Установка зависимостей

```bash
pip install -r backend/database_service/requirements.txt
```

## Конфигурация

### Переменные окружения

Скопируйте `.env.example` в `.env` и настройте:

```bash
cp backend/database_service/.env.example backend/database_service/.env
```

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_SERVICE_DB_USER` | Пользователь БД | - |
| `DATABASE_SERVICE_DB_HOST` | Хост БД | localhost |
| `DATABASE_SERVICE_DB_PORT` | Порт БД | 5432 |
| `DATABASE_SERVICE_DB_NAME` | Название БД | - |
| `DATABASE_SERVICE_DB_PASSWORD` | Пароль БД | - |
| `DATABASE_SERVICE_DB_DRIVER` | Драйвер БД | postgresql+psycopg2 |
| `DATABASE_SERVICE_POOL_SIZE` | Размер пула | 5 |
| `DATABASE_SERVICE_MAX_OVERFLOW` | Макс. перелив | 10 |
| `DATABASE_SERVICE_TESTING` | Режим тестирования | false |
| `DATABASE_SERVICE_DEBUG` | Режим отладки | false |
| `DATABASE_SERVICE_API_DOCS_ENABLED` | Документация API | true |
| `DATABASE_SERVICE_AUTO_MIGRATE` | Авто-миграции при старте | false |

### Режимы работы

**Production:**
```env
DATABASE_SERVICE_TESTING=false
DATABASE_SERVICE_DB_DRIVER=postgresql+psycopg2
```

**Testing:**
```env
DATABASE_SERVICE_TESTING=true
# Автоматически использует SQLite in-memory
```

## Использование

### Быстрый старт

```python
from backend.database_service.src import get_db_dependency

# В FastAPI приложении
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()
db_dependency = get_db_dependency()

@app.get("/users")
def get_users(db: Session = Depends(db_dependency)):
    return db.query(User).all()
```

### Получение менеджеров напрямую

```python
from backend.database_service.src import (
    get_connection_manager,
    get_session_manager,
    get_migration_runner
)

# Тест подключения
conn_manager = get_connection_manager()
if conn_manager.test_connection():
    print("БД доступна")

# Работа с сессией через контекстный менеджер
session_manager = get_session_manager()
with session_manager.get_db_context() as db:
    user = db.query(User).first()
    # auto-commit при успехе, rollback при ошибке

# Запуск миграций
migration_runner = get_migration_runner()
migration_runner.upgrade()  # до последней версии
migration_runner.downgrade("-1")  # на одну версию назад
```

### Использование в других сервисах

```python
# backend/user_service/app.py
from backend.database_service.src.container import container
from backend.database_service.src.lifespan import lifespan

app = FastAPI(lifespan=lifespan)

# Получение dependency
from backend.database_service.src import get_db_dependency
db_dependency = get_db_dependency()

@app.get("/")
def health_check(db: Session = Depends(db_dependency)):
    return {"status": "ok"}
```

## Миграции

### Создание новой миграции

```bash
cd backend/database_service
alembic revision --autogenerate -m "описание миграции"
```

### Применение миграций

```bash
alembic upgrade head
```

### Откат миграции

```bash
alembic downgrade -1
```

### Программный запуск миграций

```python
from backend.database_service.src import get_migration_runner

runner = get_migration_runner()
runner.upgrade()  # или downgrade()
```

## Архитектура

```
database_service/
├── src/
│   ├── config/          # Конфигурация БД
│   ├── connection/      # Менеджеры соединений и сессий
│   ├── container.py     # DI контейнер
│   ├── lifespan.py      # Lifespan для FastAPI
│   └── migration_runner.py  # Обёртка над Alembic
├── migrations/          # Миграции Alembic
├── requirements.txt     # Зависимости
└── app_database.py      # Точка входа
```

### Принципы

- **SRP**: Каждый класс отвечает за одну задачу
- **DIP**: Зависимости через абстракции
- **DI**: Dependency Injection через `dependency-injector`

## Тестирование

```python
import pytest
from backend.database_service.src import get_session_manager

def test_query():
    session_manager = get_session_manager()
    with session_manager.get_db_context(auto_commit=False) as db:
        result = db.execute("SELECT 1").scalar()
        assert result == 1
```

## Graceful Shutdown

Lifespan автоматически закрывает соединения при остановке приложения:

```python
from backend.database_service.src.lifespan import lifespan

app = FastAPI(lifespan=lifespan)
```

## Troubleshooting

### Ошибка подключения

1. Проверьте переменные окружения в `.env`
2. Убедитесь, что PostgreSQL запущен
3. Проверьте доступность хоста: `ping <DB_HOST>`

### Миграции не применяются

1. Проверьте путь к моделям в `migrations/env.py`
2. Убедитесь, что модели наследуются от `Base`
3. Запустите `alembic current` для проверки текущей версии

### SQLite в тестах

При `TESTING=true` автоматически используется `sqlite:///:memory:`

## Лицензия

MIT
