# User Service

Микросервис для управления пользователями платформы рецептов.

## Функционал

- Регистрация новых пользователей
- Аутентификация (вход/выход)
- Управление профилями пользователей
- JWT токены для аутентификации
- Refresh токены для продления сессии

## Структура проекта

```
user-service/
├── src/
│   │
│   ├── main.py                 # Основной файл приложения
│   ├── models.py              # SQLAlchemy модели
│   ├── schemas.py             # Pydantic схемы
│   │
│   ├── api/
│   │   └── routes.py          # API роуты
│   │
│   ├── services/
│   │   ├── auth_service.py    # Сервис аутентификации
│   │   └── user_service.py    # Сервис пользователей
│   │
│   ├── database/
│   │   └── connection.py      # Подключение к БД
│   │
│   └── middleware/
│       └── exception_handler.py # Обработчики исключений
│   
├── tests/
│   └── test_main.py           # Тесты
│   
├── requirements.txt           # Зависимости
├── Dockerfile                 # Docker конфигурация
├── run.py                     # Скрипт для запуска
└── README.md                  # Этот файл
```

## Запуск

### 1. Запуск в режиме разработки

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск базы данных (PostgreSQL)
# Создайте базу данных: createdb user_service_db

# Настройте переменные окружения (или создайте .env файл)
export DATABASE_URL="postgresql://user:password@localhost:5432/user_service_db"

# Запуск сервиса
python run.py
```

Сервис будет доступен на http://localhost:8000

### 2. Запуск через Docker

```bash
# Сборка образа
docker build -t user-service .

# Запуск контейнера
docker run -p 8001:8001 user-service
```

### 3. Запуск через docker-compose

Добавьте в корневой docker-compose.yml:

```yaml
  user-service:
    build: ./backend/services/user-service
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/user_service_db
    depends_on:
      - db
    networks:
      - app-network
```

## API Эндпоинты

### Регистрация
- **POST** `/api/v1/users/register` - Регистрация нового пользователя
- **Тело запроса**: 
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "full_name": "string (опционально)",
    "bio": "string (опционально)"
  }
  ```

### Аутентификация
- **POST** `/api/v1/users/login` - Вход пользователя
- **Тело запроса**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Ответ**:
  ```json
  {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer"
  }
  ```

### Профиль пользователя
- **GET** `/api/v1/users/me` - Получение текущего пользователя
- **PUT** `/api/v1/users/me` - Обновление профиля
- **POST** `/api/v1/users/refresh` - Обновление токена

### Администрирование
- **GET** `/api/v1/users/` - Получение списка пользователей
- **GET** `/api/v1/users/{user_id}` - Получение пользователя по ID

## Тестирование

```bash
# Установка тестовых зависимостей
pip install pytest pytest-asyncio httpx

# Запуск тестов
pytest tests/
```

## Переменные окружения

- `DATABASE_URL` - URL подключения к базе данных
- `SECRET_KEY` - Секретный ключ для JWT (по умолчанию: "your-secret-key-here-change-in-production")
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Время жизни access токена в минутах
- `REFRESH_TOKEN_EXPIRE_DAYS` - Время жизни refresh токена в днях

## Безопасность

- Пароли хешируются с использованием bcrypt
- Используются JWT токены для аутентификации
- Refresh токены хранятся в базе данных и могут быть отозваны
- CORS настроен для разработки (в продакшене нужно ограничить домены)

## Зависимости

- FastAPI - Веб-фреймворк
- SQLAlchemy - ORM для работы с базами данных
- PostgreSQL - База данных
- JWT - Токены аутентификации
- Passlib - Хеширование паролей