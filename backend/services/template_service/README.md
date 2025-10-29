# Template Service

Шаблон для создания новых микросервисов

## Структура

```
template_service/
├── src/
│   ├── api/
│   │   ├── routes.py          # API эндпоинты
│   │   └── __init__.py
│   ├── database/
│   │   ├── connection.py      # Подключение к БД (использует общую базу)
│   │   └── __init__.py
│   ├── models.py           # SQLAlchemy модели
│   ├── schemas.py          # Pydantic схемы
│   ├── services/          # Бизнес-логика
│   │   ├── template_service.py
│   │   └── __init__.py
│   ├── middleware/        # Middleware (если нужно)
│   │   ├── custom_middleware.py
│   │   └── __init__.py
│   └── __init__.py
└── main.py              # Точка входа сервиса
```

## Использование

1. Скопируйте папку `template_service` в `backend/services/`
2. Переименуйте её в соответствии с названием нового сервиса
3. Обновите импорты и настройки в файлах
4. Добавьте свои модели и бизнес-логику

## Контейнеризация

Каждый сервис должен иметь свой `Dockerfile` и быть описан в `docker-compose.yml`