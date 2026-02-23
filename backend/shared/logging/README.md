# Логирование

Централизованное логирование для всех сервисов на базе **structlog**.

## Возможности

| Компонент | Описание |
|-----------|----------|
| **Middleware** | Автоматически логирует HTTP-запросы: метод, путь, статус, время выполнения |
| **ServiceLogger** | Логирование вызовов методов сервисов с контекстом |
| **ContextLogger** | Логгер с автоматическим контекстом (layer, service, request_id) |

## Вывод в консоли

```
2025-02-23 10:15:30 [INFO] layer=http method=POST path=/auth_users/login status=success duration=0.125s request_id=a1b2c3d4
2025-02-23 10:15:31 [INFO] layer=service service=AuthService method=authenticate_and_create_tokens → Service call started args=('john',)
2025-02-23 10:15:31 [ERROR] layer=service service=AuthService method=authenticate_and_create_tokens → Service call failed error=InvalidCredentials message="Неверный пароль"
```

## Использование

### 1. Подключение middleware (main.py / app_service.py)

```python
from backend.shared.logging import LoggingMiddleware, setup_logging

# Настройка логирования (в начале приложения)
setup_logging(debug=False)  # True — подробный вывод

# Подключение middleware
app.add_middleware(LoggingMiddleware)
```

### 2. Использование в сервисах

```python
from backend.shared.logging import ServiceLogger

class AuthService:
    def __init__(self, ...):
        self.logger = ServiceLogger("AuthService")
    
    @ServiceLogger.log_call  # Автоматически логирует вызов
    def authenticate(self, user_name: str, password: str):
        # ... логика
        pass
    
    def custom_log(self):
        self.logger.info(
            "Сообщение", 
            user_id=123
            )
        self.logger.error(
            "Ошибка", 
            error="details"
            )
```

### 3. Ручной логгер

```python
from backend.shared.logging import get_logger

logger = get_logger(__name__).bind(layer="custom")
logger.info(
    "Сообщение", 
    extra="data"
    )
```

## Уровень логирования

| Параметр | Уровень | Описание |
|----------|---------|----------|
| `debug=True` | DEBUG | Подробный вывод (включая SQL, трассировки) |
| `debug=False` | INFO | Только важные события |

Изменить уровень можно в `setup_logging(debug=True/False)`.

## JSON вывод (для продакшена)

```python
setup_logging(json_output=True)  # Вывод в JSON формате
```

## Доступные компоненты

```python
from backend.shared.logging import (
    setup_logging,      # Настройка логирования
    get_logger,         # Получить логгер
    Logger,             # Тип логгера
    LoggingMiddleware,  # Middleware для FastAPI
    ServiceLogger,      # Логгер для сервисов
)
```
