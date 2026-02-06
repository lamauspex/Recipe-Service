# Новый сервисный слой

## Обзор

Новый сервисный слой построен по принципам **Clean Architecture** и обеспечивает:

- ✅ **Четкое разделение ответственности** между слоями
- ✅ **Высокую тестируемость** благодаря слабой связанности
- ✅ **Расширяемость** и простоту добавления новой функциональности
- ✅ **Единообразную обработку ошибок**
- ✅ **Современное управление зависимостями**

## Архитектура

```
services_new/
├── interfaces/          # Интерфейсы сервисов
│   ├── auth.py         # Интерфейс аутентификации
│   ├── user.py         # Интерфейс управления пользователями
│   ├── security.py     # Интерфейс безопасности
│   └── admin.py        # Интерфейс административных функций
├── usecases/           # Бизнес-логика (сценарии использования)
│   ├── auth/          # Usecases для аутентификации
│   │   ├── login.py
│   │   ├── register.py
│   │   ├── refresh_token.py
│   │   └── logout.py
│   ├── user/          # Usecases для управления пользователями
│   ├── security/      # Usecases для безопасности
│   └── admin/         # Usecases для административных функций
├── dto/               # Data Transfer Objects
│   ├── requests/      # DTO для запросов
│   └── responses/     # DTO для ответов
├── ports/             # Порт-адаптер паттерн
│   ├── repositories/  # Интерфейсы к базе данных
│   └── external/      # Интерфейсы к внешним системам
├── infrastructure/   # Реализации (адаптеры)
│   ├── repositories/  # Реализации репозиториев
│   ├── services/      # Реализации сервисов
│   └── common/        # Общие компоненты
└── decorators/       # Декораторы для cross-cutting concerns
```

## Основные компоненты

### 1. Интерфейсы (`interfaces/`)

Определяют контракты для всех сервисов:

```python
from services_new.interfaces.auth import AuthInterface
from services_new.interfaces.user import UserInterface
from services_new.interfaces.security import SecurityInterface
```

### 2. Usecases (`usecases/`)

Содержат только бизнес-логику без знания о внешних системах:

```python
from services_new.usecases.auth.login import LoginUsecase

class LoginUsecase(BaseUsecase):
    async def execute(self, request: LoginRequestDTO) -> LoginResponseDTO:
        # Только бизнес-логика
        pass
```

### 3. DTO (`dto/`)

Типизированные объекты для передачи данных:

```python
from services_new.dto.requests import LoginRequestDTO
from services_new.dto.responses import LoginResponseDTO
```

### 4. Инфраструктура (`infrastructure/`)

Реализации интерфейсов - адаптеры к внешним системам:

```python
from services_new.infrastructure.services.auth_service import AuthService
from services_new.infrastructure.repositories.user_repository import UserRepositoryAdapter
```

## Использование

### 1. Получение сервисов через DI контейнер

```python
from services_new import get_auth_service, get_security_service

# В FastAPI dependencies
async def get_auth_dependency():
    return get_auth_service()

# Использование в роутере
@auth_router.post("/login")
async def login(
    request: LoginRequest,
    auth_service: AuthInterface = Depends(get_auth_dependency)
):
    response = await auth_service.login(request)
    return response
```

### 2. Создание нового usecase

```python
# 1. Создаем DTO
# services_new/dto/requests/my_request.py
class MyRequestDTO(BaseRequestDTO):
    data: str

# services_new/dto/responses/my_response.py  
class MyResponseDTO(BaseResponseDTO):
    result: str

# 2. Создаем usecase
# services_new/usecases/my_feature/my_usecase.py
class MyUsecase(BaseUsecase):
    async def execute(self, request: MyRequestDTO) -> MyResponseDTO:
        # Бизнес-логика
        result = self._process_data(request.data)
        return MyResponseDTO(data={"result": result})
```

### 3. Создание нового сервиса

```python
# 1. Определяем интерфейс
# services_new/interfaces/my_service.py
class MyServiceInterface(ABC):
    @abstractmethod
    async def do_something(self, request: MyRequestDTO) -> MyResponseDTO:
        pass

# 2. Реализуем в инфраструктуре
# services_new/infrastructure/services/my_service.py
class MyService(MyServiceInterface):
    def __init__(self, my_usecase):
        self.my_usecase = my_usecase
    
    async def do_something(self, request: MyRequestDTO) -> MyResponseDTO:
        return await self.my_usecase.execute(request)

# 3. Регистрируем в DI контейнере
# services_new/di_container.py
my_usecase = providers.Factory(MyUsecase, dependency1=..., dependency2=...)
my_service = providers.Factory(MyService, my_usecase=my_usecase)
```

## Преимущества новой архитектуры

### 1. **Разделение ответственности**
- **Usecases** - только бизнес-логика
- **Services** - только адаптация к внешним системам
- **DTO** - только передача данных

### 2. **Инверсия зависимостей**
```
API Layer → Interfaces → Usecases → Repositories → Database
                ↓
            Infrastructure
```

### 3. **Тестируемость**
```python
# Легко мокировать зависимости
@pytest.mark.asyncio
async def test_login():
    user_repo = AsyncMock()
    security_service = AsyncMock()
    
    usecase = LoginUsecase(
        user_repository=user_repo,
        security_service=security_service
    )
    
    response = await usecase.execute(request)
    assert response.success == True
```

### 4. **Расширяемость**
- Легко добавлять новые usecases
- Легко заменять реализации (например, базу данных)
- Легко добавлять cross-cutting concerns через декораторы

## Миграция с старого сервиса

### Шаги миграции:

1. **Создать соответствующие usecases** в новом сервисе
2. **Обновить API роутеры** для использования нового DI контейнера
3. **Протестировать** новую функциональность
4. **Постепенно отключить** старый сервис
5. **Удалить** старый сервис после полной миграции

### Пример миграции API роутера:

```python
# Старый роутер
@auth_router.post("/login")
async def login_old(request: LoginRequest):
    auth_service = get_auth_service_old()  # Старый сервис
    return await auth_service.login(request)

# Новый роутер  
@auth_router.post("/login")
async def login_new(request: LoginRequest):
    auth_service = get_auth_service()  # Новый сервис
    return await auth_service.login(request)
```

## Тестирование

### Unit тесты usecases:

```python
import pytest
from services_new.usecases.auth.login import LoginUsecase
from services_new.dto.requests import LoginRequestDTO
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_login_success():
    # Мок зависимостей
    user_repo = AsyncMock()
    security_service = AsyncMock()
    token_repo = AsyncMock()
    
    # Настройка моков
    user_repo.get_by_email.return_value = mock_user
    security_service.verify_password.return_value = True
    
    # Выполнение
    usecase = LoginUsecase(
        user_repository=user_repo,
        security_service=security_service,
        token_repository=token_repo
    )
    
    request = LoginRequestDTO(email="test@example.com", password="password")
    response = await usecase.execute(request)
    
    # Проверка
    assert response.success == True
    assert "tokens" in response.data
```

### Integration тесты:

```python
@pytest.mark.asyncio
async def test_auth_service_integration():
    auth_service = get_auth_service()
    
    # Регистрация
    register_request = RegisterRequestDTO(
        email="test@example.com",
        password="password123",
        first_name="Test",
        last_name="User"
    )
    
    register_response = await auth_service.register(register_request)
    assert register_response.success == True
    
    # Авторизация
    login_request = LoginRequestDTO(
        email="test@example.com",
        password="password123"
    )
    
    login_response = await auth_service.login(login_request)
    assert login_response.success == True
    assert "tokens" in login_response.data
```

## Заключение

Новый сервисный слой обеспечивает:

- 🎯 **Чистую архитектуру** с четким разделением слоев
- 🧪 **Высокую тестируемость** благодаря слабой связанности  
- 🚀 **Простоту расширения** новой функциональности
- 🔧 **Легкость поддержки** и отладки
- 📊 **Единообразную обработку ошибок**
- ⚡ **Современные практики** разработки

Это создает прочную основу для дальнейшего развития приложения и упрощает командную разработку.