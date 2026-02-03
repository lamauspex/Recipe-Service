# User Service - Современный сервис управления пользователями

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Описание

**User Service** — это современный, масштабируемый микросервис для управления пользователями, построенный на FastAPI. Сервис предоставляет полнофункциональную систему аутентификации, авторизации, управления ролями и безопасности корпоративного уровня.

### ✨ Ключевые особенности

- 🔐 **Комплексная система безопасности**: JWT токены, refresh tokens, rate limiting, блокировка аккаунтов
- 👥 **Гибкая система ролей**: Многоуровневая система разрешений с поддержкой множественных ролей
- 🛡️ **Защита от атак**: Детекция подозрительной активности, блокировка IP, защита от брутфорса
- 📊 **Аналитика и мониторинг**: Подробная статистика входов, активности пользователей
- 🔄 **Современная архитектура**: Clean Architecture, Repository Pattern, Dependency Injection
- 📝 **Автоматическая документация**: Swagger/OpenAPI, ReDoc
- ✅ **Полное покрытие тестами**: Модульные и интеграционные тесты

## 🏗️ Архитектура

Проект построен на принципах **Clean Architecture** с четким разделением ответственности:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer     │    │  Service Layer  │    │ Repository Layer│
│   (Routers)     │◄──►│   (Business)    │◄──►│    (Data)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Middleware    │    │   Security      │    │   Database      │
│   (Cross-cut)   │    │   Services      │    │   (SQLAlchemy)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🗂️ Структура проекта

```
user_service/
├── api/                    # API роутеры
│   ├── api_auth/          # Аутентификация
│   ├── api_admin/         # Администрирование
│   ├── api_user/          # Управление пользователями
│   └── api_role/          # Управление ролями
├── services/              # Бизнес-логика
│   ├── auth_service/      # Аутентификация
│   ├── security_service/  # Безопасность
│   ├── admin_service/     # Администрирование
│   └── user_service/      # Пользователи
├── repository/           # Доступ к данным
├── models/               # Модели данных
├── schemas/              # Схемы Pydantic
├── middleware/           # Middleware компоненты
├── config/              # Конфигурация
├── exceptions/          # Обработка исключений
└── utils/               # Утилиты
```

## 🚦 Быстрый старт

### Требования

- Python 3.9+
- PostgreSQL 12+
- Redis (опционально, для кэширования)

### Установка

1. **Клонирование репозитория**
   ```bash
   git clone <repository-url>
   cd user_service
   ```

2. **Создание виртуального окружения**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

3. **Установка зависимостей**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройка переменных окружения**
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл с вашими настройками
   ```

5. **Запуск миграций базы данных**
   ```bash
   alembic upgrade head
   ```

6. **Запуск сервера**
   ```bash
   python main.py
   ```

Сервис будет доступен по адресу: `http://localhost:8000`

## 📚 Документация

- **[API Документация](./API_DOCUMENTATION.md)** — Подробное описание всех API endpoints
- **[Архитектура](./ARCHITECTURE.md)** — Детальное описание архитектурных решений
- **[Безопасность](./SECURITY.md)** — Система безопасности и защиты

## 🔧 Конфигурация

Основные параметры конфигурации находятся в файлах `user_service/config/`:

- **API**: Настройки FastAPI, документация
- **Auth**: JWT настройки, время жизни токенов
- **Database**: Подключение к БД, миграции
- **Cache**: Настройки Redis/кэширования
- **Monitoring**: Логирование, метрики

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# С покрытием кода
pytest --cov=user_service

# Конкретный тест
pytest tests/tests_MODELS/test_user_models.py
```

## 🛡️ Безопасность

Сервис включает многоуровневую систему безопасности:

- **Аутентификация**: JWT + Refresh Tokens
- **Авторизация**: Система ролей и разрешений
- **Rate Limiting**: Защита от DoS атак
- **Account Locking**: Блокировка подозрительных аккаунтов
- **IP Blocking**: Блокировка вредоносных IP
- **Suspicious Detection**: Детекция аномального поведения

Подробности в [документации по безопасности](./SECURITY.md).

## 📊 Мониторинг

- **Health Check**: `/health` endpoint
- **Metrics**: Интеграция с Prometheus
- **Structured Logging**: JSON логи с trace_id
- **Error Tracking**: Централизованная обработка ошибок

## 🤝 Вклад в проект

1. Fork проекта
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 👥 Команда

Разработано командой **NLP-Core-Team** — экспертами в области разработки высоконагруженных систем и машинного обучения.

---

⭐ **Если проект полезен, поставьте звездочку!**