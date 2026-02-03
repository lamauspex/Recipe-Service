# Архитектура User Service

## 🏗️ Общий обзор

User Service построен на принципах **Clean Architecture** с четким разделением ответственности между слоями. Архитектура следует принципам SOLID и обеспечивает высокую тестируемость, поддерживаемость и масштабируемость.

### 🎯 Ключевые принципы

- **Separation of Concerns**: Четкое разделение ответственности между слоями
- **Dependency Inversion**: Зависимости направлены внутрь, к ядру приложения
- **Single Responsibility**: Каждый компонент имеет одну зону ответственности
- **Open/Closed**: Открыт для расширения, закрыт для модификации
- **Testability**: Все компоненты легко тестируются изолированно

## 📐 Слоистая архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   API Routes    │ │   Middleware    │ │   Schemas       ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │ depends on
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │  Auth Service   │ │ Security Service│ │ Admin Service   ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │ depends on
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │  User Model     │ │   Role Model    │ │   Token Model   ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │ uses
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                      │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │ Repository      │ │  Database ORM   │ │   Config        ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### Аутентификация пользователя
```
Client → API Router → Auth Service → User Repository → Database
    ↑                                              ↓
    ← JWT Service ← Security Service ← Response ←──┘
```

### Создание пользователя
```
Client → API Router → User Service → Security Check → Repository → Database
    ↑                                                    ↓
    ← Validation ← Email Service ← Response ←───────────┘
```

## 📁 Структура модулей

### API Layer (Presentation)
**Расположение**: `user_service/api/`

**Назначение**: Входная точка для HTTP запросов, валидация данных, сериализация ответов.

**Компоненты**:
- **Routers**: FastAPI роутеры для группировки endpoints
- **Schemas**: Pydantic модели для валидации входных/выходных данных
- **Middleware**: Cross-cutting concerns (CORS, логирование, аутентификация)

**Пример структуры**:
```
api/
├── __init__.py
├── api_auth/
│   ├── auth_routers.py      # /auth/login, /auth/refresh
│   └── register_user.py      # /auth/register
├── api_admin/
│   ├── user_management_routers.py  # /admin/users/*
│   ├── statistics_analytics_routers.py  # /admin/stats/*
│   └── safety_routers.py     # /admin/safety/*
├── api_user/
│   └── management_routers.py # /users/profile
└── api_role/
    ├── roles_routers.py      # /roles/*
    └── permissions_routers.py # /roles/permissions/*
```

### Application Layer
**Расположение**: `user_service/services/`

**Назначение**: Бизнес-логика, координация операций между репозиториями.

**Принципы**:
- Каждый сервис инкапсулирует определенную бизнес-функцию
- Сервисы не зависят друг от друга напрямую
- Используют Repository Pattern для доступа к данным

**Ключевые сервисы**:

#### AuthService
```python
class AuthService:
    def authenticate_user(self, username: str, password: str) -> Optional[User]
    def create_tokens(self, user: User) -> Tuple[str, str]
    def refresh_access_token(self, refresh_token: str) -> Optional[Tuple[str, str]]
```

#### SecurityService
```python
class SecurityService:
    def check_security(self, email: str, ip_address: str, user_agent: str) -> tuple[bool, Optional[str]]
    def is_rate_limited(self, identifier: str) -> bool
    def detect_suspicious_activity(self, email: str, user_agent: str) -> bool
```

### Domain Layer
**Расположение**: `user_service/models/`

**Назначение**: Бизнес-объекты и правила, независимые от инфраструктуры.

**Компоненты**:
- **Models**: SQLAlchemy модели для работы с БД
- **Mixins**: Переиспользуемые компоненты (BaseModel, TimeMixin, StatusMixin)
- **Decorators**: Валидаторы и конвертеры типов

**Пример модели**:
```python
class User(BaseModel):
    user_name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Связи
    roles: Mapped[List["RoleModel"]] = relationship(
        "RoleModel",
        secondary="user_roles",
        back_populates="users"
    )
    
    # Бизнес-методы
    def has_permission(self, permission: int) -> bool:
        return bool(self.all_permissions & permission)
```

### Infrastructure Layer
**Расположение**: `user_service/repository/`, `user_service/config/`

**Назначение**: Техническая реализация доступа к данным, внешним сервисам и конфигурации.

**Repository Pattern**:
```python
class UserRepository:
    def __init__(self, db_session):
        self.session = db_session
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter(User.user_name == username).first()
    
    def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        self.session.add(user)
        self.session.commit()
        return user
```

## 🔧 Конфигурация

### Централизованная конфигурация
```python
class Settings:
    def __init__(self):
        self.auth = auth_config
        self.database = database_config
        self.api = api_config
        self.cache = cache_config
        self.monitoring = monitoring_config
```

### Модульная конфигурация
- **API Config**: FastAPI настройки, документация
- **Auth Config**: JWT параметры, время жизни токенов
- **Database Config**: Подключение к БД, миграции
- **Cache Config**: Redis, кэширование
- **Monitoring Config**: Логирование, метрики

## 🛡️ Middleware Architecture

### Слой Middleware
```
┌─────────────────────────────────────┐
│         FastAPI Application         │
├─────────────────────────────────────┤
│  CORS Middleware                    │
│  Security Headers Middleware        │
│  Rate Limiting Middleware           │
│  Authentication Middleware          │
│  Logging Middleware                 │
│  Exception Handling Middleware      │
├─────────────────────────────────────┤
│         Business Logic              │
└─────────────────────────────────────┘
```

### Ключевые Middleware

#### Security Middleware
- **CORS**: Настройки CORS политики
- **Headers**: Security headers (HSTS, CSP, X-Frame-Options)
- **Rate Limiting**: Ограничение запросов по IP/пользователю

#### Auth Middleware
- **JWT Authentication**: Извлечение и валидация JWT токенов
- **Dependency Injection**: Внедрение текущего пользователя в endpoints

#### Logging Middleware
- **Request/Response Logging**: Структурированное логирование HTTP запросов
- **Business Logging**: Логирование бизнес-событий
- **Trace ID**: Трассировка запросов через систему

## 🔄 Паттерны проектирования

### 1. Repository Pattern
**Цель**: Абстрагирование доступа к данным от бизнес-логики.

```python
# Сервис использует репозиторий
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def get_active_users(self) -> List[User]:
        return self.user_repo.get_users_by_status('active')
```

### 2. Service Layer Pattern
**Цель**: Инкапсуляция бизнес-логики в сервисах.

```python
class AuthService:
    def login(self, username: str, password: str):
        # 1. Проверка безопасности
        if not self.security_service.check_security(username):
            raise SecurityException("Security check failed")
        
        # 2. Аутентификация
        user = self.user_repo.get_by_username(username)
        if not self.password_service.verify(password, user.hashed_password):
            raise AuthException("Invalid credentials")
        
        # 3. Создание токенов
        tokens = self.jwt_service.create_tokens(user)
        
        # 4. Логирование
        self.logger.info(f"User {username} logged in")
        
        return tokens
```

### 3. Factory Pattern
**Цель**: Создание объектов с конфигурацией.

```python
class MiddlewareFactory:
    @staticmethod
    def create_security_middleware(config: SecurityConfig):
        return [
            CORSMiddleware(config.cors),
            SecurityHeadersMiddleware(config.headers),
            RateLimitMiddleware(config.rate_limit)
        ]
```

### 4. Dependency Injection
**Цель**: Управление зависимостями и тестирование.

```python
def create_app() -> FastAPI:
    app = FastAPI()
    
    # Внедрение зависимостей
    app.dependency_overrides[UserRepository] = lambda: UserRepository(db)
    app.dependency_overrides[AuthService] = lambda: AuthService(db)
    
    return app
```

## 📊 Database Design

### Миграции
Проект использует Alembic для управления схемой базы данных:

```
migrations/
├── versions/
│   ├── a7c53b6c4d00_initial_migration.py
│   └── ...
├── env.py
└── script.py.mako
```

### Модели данных

#### User Model
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_name VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    bio TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Role Model
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id),
    role_id UUID REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);
```

### Миксины для моделей

#### BaseMixin
```python
class BaseMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
```

#### StatusMixin
```python
class StatusMixin:
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
```

## 🚀 Масштабирование

### Горизонтальное масштабирование
- **Stateless Design**: Сервис не хранит состояние между запросами
- **Load Balancing**: Поддержка multiple instances
- **Database Connection Pooling**: Эффективное использование соединений с БД

### Вертикальное масштабирование
- **Async/Await**: Асинхронная обработка запросов
- **Connection Pooling**: Пулы соединений для БД и Redis
- **Caching**: Многоуровневое кэширование

### Производительность
- **Database Indexing**: Индексы на часто используемые поля
- **Query Optimization**: Оптимизированные запросы с eager loading
- **Pagination**: Пагинация для больших списков
- **Rate Limiting**: Защита от злоупотреблений

## 🔍 Мониторинг и наблюдаемость

### Логирование
```python
import structlog

logger = structlog.get_logger()

# Структурированное логирование
logger.info(
    "User logged in",
    user_id=user.id,
    username=user.username,
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent")
)
```

### Метрики
- **Business Metrics**: Количество пользователей, успешных входов
- **Technical Metrics**: Время ответа, ошибки, использование ресурсов
- **Security Metrics**: Заблокированные IP, подозрительная активность

### Health Checks
```python
@app.get("/health")
async def health_check():
    db_status = await check_database_connection()
    cache_status = await check_redis_connection()
    
    return {
        "status": "healthy" if all([db_status, cache_status]) else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "cache": "connected" if cache_status else "disconnected"
    }
```

## 🧪 Тестирование

### Стратегия тестирования
```
┌─────────────────────────────────────┐
│         Test Pyramid                │
├─────────────────────────────────────┤
│  Unit Tests    ████ (80%)          │
│  Integration   ██   (15%)           │
│  E2E Tests     █     (5%)           │
└─────────────────────────────────────┘
```

### Структура тестов
```
tests/
├── conftest.py              # Общие фикстуры
├── tests_MODELS/            # Модульные тесты моделей
├── tests_CONFIG/            # Тесты конфигурации
├── tests_API/               # Интеграционные тесты API
└── tests_INTEGRATION/       # E2E тесты
```

### Пример теста
```python
@pytest.mark.asyncio
async def test_user_registration():
    # Arrange
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "secure_password"
    }
    
    # Act
    response = await client.post("/api/v1/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["user_id"] is not None
```

## 🔧 Развертывание

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app_users", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration
```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/user_service
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
DEBUG=false
```

Эта архитектура обеспечивает:
- ✅ **Модульность**: Легкое добавление новой функциональности
- ✅ **Тестируемость**: Каждый компонент тестируется изолированно
- ✅ **Поддерживаемость**: Четкое разделение ответственности
- ✅ **Масштабируемость**: Горизонтальное и вертикальное масштабирование
- ✅ **Безопасность**: Многоуровневая система защиты