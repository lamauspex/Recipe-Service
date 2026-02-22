# Путь регистрации пользователя

## Обзор

Документация описывает полный путь запроса при регистрации пользователя — от HTTP-запроса до сохранения в БД.

---

## 1. HTTP Request → API Router

**Файл:** `backend/user_service/src/api/register_user.py`

```
POST /api/v1/auth/register_users/register
```

### Входящие данные:
- **Content-Type:** `application/json`
- **Body:** `UserCreate` (Pydantic schema)

### Код:
```python
@router.post(
    "/register",
    summary="Регистрация пользователя",
    response_model=UserResponseDTO
)
async def register_user(
    register_data: UserCreate,
    register_service: RegisterService = Depends(get_register_service)
):
    return register_service.register_user(register_data)
```

### Что происходит:
1. FastAPI принимает JSON-запрос
2. Pydantic валидирует данные через `UserCreate` schema
3. `Depends(get_register_service)` создаёт экземпляр `RegisterService`
4. Вызывается метод `register_service.register_user(register_data)`

---

## 2. Schema: UserCreate

**Файл:** `backend/user_service/src/schemas/register/register_request.py`

### Структура:
```python
class UserCreate(NameValidatedModel, EmailValidatedModel, PasswordValidatedModel):
    """Схема для создания пользователя"""
    user_name: str
    email: EmailStr
    password: str
    full_name: str
```

### Наследуемые валидаторы:
| Модель | Поле | Валидация |
|--------|------|-----------|
| NameValidatedModel | user_name | Проверка длины (3-50), алфавит + цифры + _ |
| EmailValidatedModel | email | Валидация EmailStr + нормализация в нижний регистр |
| PasswordValidatedModel | password | Минимум 8 символов, сложность |
| FullNameValidatedModel | full_name | Длина 1-200 символов |

### Результат:
Если данные валидны — создаётся объект `UserCreate` и передаётся в сервис.

---

## 3. Service: RegisterService

**Файл:** `backend/user_service/src/service/register_service/register_service.py`

### Метод: `register_user(user_data: UserCreate) -> UserResponseDTO`

```python
def register_user(self, user_data: UserCreate) -> UserResponseDTO:
    # 1. Проверка существования пользователя
    existing_user = self._check_user_exists(user_data)
    
    # 2. Конвертация в DTO (с хешированием пароля)
    user_dto = self._create_dto(user_data)
    
    # 3. Сохранение в БД через репозиторий
    created_user = self.user_repo.create_user_with_default_role(
        user_dto.to_repository_dict()
    )
    
    # 4. Конвертация в ответный DTO
    return self._create_response(created_user)
```

### Этапы:
1. **Проверка уникальности** — ищет пользователя с таким же `user_name` или `email`
2. **Маппинг** — `UserCreate` → `UserRegistrationDTO` (пароль хешируется)
3. **Сохранение** — вызов репозитория
4. **Ответ** — `User` → `UserResponseDTO`

---

## 4. Mapper: UserRegistrationMapper

**Файл:** `backend/user_service/src/service/register_service/mappers.py`

### Метод: `api_to_dto(user_create: UserCreate) -> UserRegistrationDTO`

```python
def api_to_dto(self, user_create: UserCreate) -> UserRegistrationDTO:
    hashed_password = self.password_service.hash_password(user_create.password)
    
    return UserRegistrationDTO(
        user_name=user_create.user_name,
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=hashed_password,
        role_name="user",
        is_active=True,
        email_verified=False
    )
```

### Что делает:
- Принимает `UserCreate` (с чистым паролем)
- Хеширует пароль через `PasswordService`
- Создаёт `UserRegistrationDTO` с ролью "user" по умолчанию

### Метод: `model_to_response_dto(user: User) -> UserResponseDTO`

```python
@staticmethod
def model_to_response_dto(user: User) -> UserResponseDTO:
    role = user.role
    permission_names = [perm_name for perm_name, perm_value in ...]
    
    return UserResponseDTO(
        id=str(user.id),
        user_name=user.user_name,
        email=user.email,
        full_name=user.full_name,
        ...
    )
```

---

## 5. DTO: UserRegistrationDTO

**Файл:** `backend/user_service/src/schemas/register/register_dto.py`

### Структура:
```python
class UserRegistrationDTO(
    DTOConverterMixin,
    NameValidatedModel,
    EmailValidatedModel,
    HashedPasswordValidatedModel,
    FullNameValidatedModel,
    UserStatusModel,
    UserTimestampsModel,
    RoleNameValidatedModel
):
    user_name: str
    email: EmailStr
    full_name: str
    hashed_password: str
    role_name: str = "user"
    is_active: bool = True
    email_verified: bool = False
    created_at: datetime
    updated_at: datetime
```

### Метод: `to_repository_dict() -> dict`

```python
def to_repository_dict(self) -> dict:
    return super().to_repository_dict(exclude={'created_at', 'updated_at'})
```

Возвращает словарь для репозитория (исключая служебные поля).

---

## 6. Repository: SQLUserRepository

**Файл:** `backend/user_service/src/repositories/sql_user_repository.py`

### Метод: `create_user_with_default_role(user_data: dict) -> User`

```python
def create_user_with_default_role(self, user_data: dict) -> User:
    role_name = user_data.get('role_name', 'user')
    
    # Проверка допустимости роли
    from backend.shared.models.identity.role import ROLES
    if role_name not in ROLES:
        raise ConflictException(...)
    
    # Создание модели SQLAlchemy
    user = User(**user_data)
    
    self.db.add(user)
    self.db.commit()
    self.db.refresh(user)
    return user
```

### Что делает:
1. Проверяет, что роль существует в справочнике `ROLES`
2. Создаёт SQLAlchemy модель `User`
3. Сохраняет в БД (add + commit)
4. Возвращает созданного пользователя с ID

---

## 7. Model: User

**Файл:** `backend/shared/models/identity/user.py`

### Структура (SQLAlchemy):
```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    full_name: Mapped[str]
    hashed_password: Mapped[str]
    role_name: Mapped[str] = mapped_column(default="user")
    is_active: Mapped[bool] = mapped_column(default=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    login_count: Mapped[int] = mapped_column(default=0)
    last_login: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), 
        onupdate=func.now()
    )
    
    role: Mapped["Role"] = relationship("Role", back_populates="users")
```

---

## 8. Response: UserResponseDTO

**Файл:** `backend/user_service/src/schemas/register/register_response.py`

### Структура:
```python
class UserResponseDTO(BaseModel):
    id: str
    user_name: str
    email: str
    full_name: str
    is_active: bool
    email_verified: bool
    role_name: str
    role_display_name: str
    permissions: List[str]
    login_count: int
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime
```

---

## Диаграмма потока данных

```
HTTP Request (JSON)
        │
        ▼
┌───────────────────┐
│  API Router       │  register_user.py
│  POST /register   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Pydantic Schema  │  UserCreate (валидация)
│  UserCreate       │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  RegisterService  │  register_service.py
│  .register_user() │
└────────┬──────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌────────────┐
│Mapper │ │ Repository │
│DTO    │ │ Проверка   │
└───┬───┘ └──────┬─────┘
    │            │
    ▼            ▼
┌───────────────────┐
│  SQLUserRepository│  sql_user_repository.py
│  .create_user()   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  SQLAlchemy       │
│  User Model       │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  PostgreSQL       │
│  (INSERT)         │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  UserResponseDTO  │  (обратная конвертация)
│  HTTP Response    │
└───────────────────┘
```

---

## ⚠️ НАЙДЕННАЯ ПРОБЛЕМА

### Симптом:
В Swagger `/docs` при попытке вызвать регистрацию:
```
For 'args': Required field is not provided.
For 'kwargs': Required field is not provided.
```

### Причина:
В файле `backend/database_service/src/container.py`:

```python
# Проблема в get_db_dependency()
def get_db_dependency():
    return container.db_dependency  # ❌ Возвращает объект Factory, не функцию!
```

`container.db_dependency` — это объект `providers.Factory`, а не callable-функция. FastAPI `Depends()` не может определить сигнатуру и показывает `args` и `kwargs`.

### Решение:

**Вариант 1 (рекомендуется):** Изменить `backend/database_service/src/container.py`:

```python
def get_db_dependency():
    return container.db_dependency()  # ✅ Вызвать фабрику!
```

**Вариант 2:** Создать обёртку-функцию:

```python
def get_db_dependency():
    def db_session():
        return next(container.db_dependency())
    return db_session
```

---

## Зависимости (Dependencies)

Для работы регистрации требуются:

| Dependency | Источник | Назначение |
|------------|----------|------------|
| `get_db_dependency` | database_service/container.py | Получение сессии БД |
| `get_user_repository` | user_service/dependencies.py | Создание SQLUserRepository |
| `get_register_service` | user_service/dependencies.py | Создание RegisterService |
| `container.password_service()` | user_service/container.py | Хеширование пароля |
| `container.auth_config()` | user_service/container.py | Конфигурация auth |
