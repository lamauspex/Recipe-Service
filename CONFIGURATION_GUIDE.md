# Гайд по конфигурации микросервисной архитектуры

## Обзор файлов конфигурации

### Основные файлы:
- **`.env`** - текущая конфигурация (разработка)
- **`.env.example`** - шаблон для создания новой конфигурации
- **`.env.test`** - конфигурация для тестового окружения
- **`.env.production.example`** - шаблон для продакшена

## Быстрая настройка

### 1. Настройка базы данных

Перед запуском сервисов убедитесь, что PostgreSQL запущен и доступен:

```bash
# Проверка подключения к PostgreSQL
psql -h localhost -p 5432 -U postgres -c "SELECT version();"
```

### 2. Создание ОДНОЙ общей базы данных

```sql
-- Подключитесь к PostgreSQL и выполните:
CREATE DATABASE recipe_app;
```

### 3. Настройка файла .env

Откройте файл `.env` и убедитесь, что настройки соответствуют вашему окружению:

```env
DB_USER=postgres
DB_PASSWORD=258074
DB_HOST=localhost
DB_PORT=5432
DB_NAME=recipe_app  # ОДНА ОБЩАЯ БАЗА
```

### 4. Запуск сервисов

Каждый сервис можно запустить отдельно:

```bash
# Запуск user-service
cd backend/services/user_service/src
python main.py

# Запуск recipe-service (в другом терминале)
cd backend/services/recipe_service/src
python main.py

# И т.д.
```

## Тестирование подключения

### Проверка каждого сервиса:

```bash
# Проверка user-service
cd backend/services/user_service/src
python -c "from database.connection import test_connection; test_connection()"

# Проверка recipe-service
cd backend/services/recipe_service/src
python -c "from database.connection import test_connection; test_connection()"
```

### Инициализация базы данных:

```bash
# Инициализация user-service (создает таблицы users и refresh_tokens)
cd backend/services/user_service/src
python -c "from database.connection import init_db; init_db()"

# Инициализация recipe-service (создает таблицы recipes, ingredients и т.д.)
cd backend/services/recipe_service/src
python -c "from database.connection import init_db; init_db()"
```

## Тестовый режим

Для запуска тестов используйте один из вариантов:

### Вариант 1: Использовать основной .env
```bash
pytest tests/
```

### Вариант 2: Переопределить переменные
```bash
export TESTING=True
pytest tests/
```

## Особенности архитектуры

### Независимость сервисов в ОДНОЙ БАЗЕ

Каждый сервис имеет:
- Свои таблицы в общей базе данных
- Свои модели и схемы
- Автономное подключение к БД

### Преимущества одной базы данных:
✅ **Простота управления** - одна база, одно резервное копирование  
✅ **Транзакционность** - возможность сложных транзакций  
✅ **Простота развертывания** - меньше компонентов для настройки  

### Переменные окружения

Сервисы используют следующие переменные:

- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - общие настройки БД
- `DB_NAME` - ОБЩАЯ база данных для всех сервисов
- `{SERVICE_NAME}_PORT` - порт для сервиса

## Решение проблем

### Ошибка подключения к БД

Если возникли проблемы с подключением:

1. **Проверьте настройки PostgreSQL**
2. **Убедитесь, что база данных создана**
3. **Проверьте файл .env**

## Дальнейшие шаги

После успешной настройки можно:

1. **Настроить API Gateway** для коммуникации между сервисами
2. **Реализовать Docker-конфигурацию**
3. **Настроить мониторинг и логирование**