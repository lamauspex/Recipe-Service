# API Documentation - User Service

## 📋 Содержание

- [Аутентификация](#аутентификация)
- [Управление пользователями](#управление-пользователями)
- [Управление ролями](#управление-ролями)
- [Администрирование](#администрирование)
- [Безопасность](#безопасность)
- [Статистика](#статистика)
- [Здоровье системы](#здоровье-системы)

## 🔐 Аутентификация

### POST `/api/v1/auth/login`

Аутентификация пользователя и получение токенов доступа.

**Request Body:**
```json
{
    "user_name": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
        "id": "uuid",
        "user_name": "string",
        "email": "string",
        "full_name": "string",
        "roles": ["string"]
    }
}
```

**Статусы ошибок:**
- `401`: Неверные учетные данные
- `423`: Аккаунт заблокирован
- `429`: Превышен лимит запросов

### POST `/api/v1/auth/register`

Регистрация нового пользователя.

**Request Body:**
```json
{
    "user_name": "string",
    "email": "string",
    "password": "string",
    "full_name": "string",
    "bio": "string"
}
```

**Response:**
```json
{
    "message": "User registered successfully",
    "user_id": "uuid",
    "verification_required": true
}
```

### POST `/api/v1/auth/refresh`

Обновление access token с помощью refresh token.

**Request Body:**
```json
{
    "refresh_token": "string"
}
```

**Response:**
```json
{
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer",
    "expires_in": 3600
}
```

## 👥 Управление пользователями

### GET `/api/v1/users/profile`

Получение профиля текущего пользователя.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
    "id": "uuid",
    "user_name": "string",
    "email": "string",
    "full_name": "string",
    "bio": "string",
    "email_verified": "boolean",
    "last_login": "datetime",
    "login_count": "integer",
    "roles": [
        {
            "id": "uuid",
            "name": "string",
            "description": "string",
            "permissions": "integer"
        }
    ],
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### PUT `/api/v1/users/profile`

Обновление профиля пользователя.

**Request Body:**
```json
{
    "full_name": "string",
    "bio": "string"
}
```

### POST `/api/v1/auth/change-password`

Смена пароля пользователя.

**Request Body:**
```json
{
    "current_password": "string",
    "new_password": "string"
}
```

## 🏢 Управление ролями

### GET `/api/v1/roles`

Получение списка всех ролей (только для администраторов).

**Response:**
```json
{
    "roles": [
        {
            "id": "uuid",
            "name": "string",
            "description": "string",
            "permissions": "integer",
            "user_count": "integer",
            "created_at": "datetime"
        }
    ]
}
```

### POST `/api/v1/roles`

Создание новой роли.

**Request Body:**
```json
{
    "name": "string",
    "description": "string",
    "permissions": "integer"
}
```

### PUT `/api/v1/roles/{role_id}`

Обновление роли.

### DELETE `/api/v1/roles/{role_id}`

Удаление роли.

### POST `/api/v1/roles/permissions/check`

Проверка разрешений пользователя.

**Request Body:**
```json
{
    "user_id": "uuid",
    "permission": "integer"
}
```

## ⚙️ Администрирование

### GET `/api/v1/admin/users`

Получение списка пользователей с пагинацией и фильтрацией.

**Query Parameters:**
- `page`: Номер страницы (по умолчанию: 1)
- `size`: Размер страницы (по умолчанию: 20)
- `search`: Поиск по имени или email
- `role`: Фильтр по роли
- `status`: Фильтр по статусу (active/inactive)

**Response:**
```json
{
    "users": [
        {
            "id": "uuid",
            "user_name": "string",
            "email": "string",
            "full_name": "string",
            "is_active": "boolean",
            "email_verified": "boolean",
            "last_login": "datetime",
            "login_count": "integer",
            "roles": ["string"],
            "created_at": "datetime"
        }
    ],
    "pagination": {
        "page": "integer",
        "size": "integer",
        "total": "integer",
        "pages": "integer"
    }
}
```

### GET `/api/v1/admin/users/{user_id}`

Получение детальной информации о пользователе.

### PUT `/api/v1/admin/users/{user_id}`

Обновление информации о пользователе.

**Request Body:**
```json
{
    "user_name": "string",
    "email": "string",
    "full_name": "string",
    "is_active": "boolean",
    "roles": ["string"]
}
```

### DELETE `/api/v1/admin/users/{user_id}`

Удаление пользователя (мягкое удаление).

### POST `/api/v1/admin/users/{user_id}/activate`

Активация пользователя.

### POST `/api/v1/admin/users/{user_id}/deactivate`

Деактивация пользователя.

### POST `/api/v1/admin/users/{user_id}/reset-password`

Сброс пароля пользователя (генерация токена).

## 🛡️ Безопасность

### GET `/api/v1/admin/safety/blocked-ips`

Получение списка заблокированных IP адресов.

**Response:**
```json
{
    "blocked_ips": [
        {
            "ip_address": "string",
            "blocked_at": "datetime",
            "reason": "string",
            "blocked_by": "string"
        }
    ]
}
```

### POST `/api/v1/admin/safety/block-ip`

Блокировка IP адреса.

**Request Body:**
```json
{
    "ip_address": "string",
    "reason": "string",
    "duration_hours": "integer"
}
```

### DELETE `/api/v1/admin/safety/blocked-ips/{ip_id}`

Разблокировка IP адреса.

### GET `/api/v1/admin/safety/locked-accounts`

Получение списка заблокированных аккаунтов.

**Response:**
```json
{
    "locked_accounts": [
        {
            "user_id": "uuid",
            "user_name": "string",
            "email": "string",
            "locked_at": "datetime",
            "reason": "string",
            "locked_until": "datetime",
            "failed_attempts": "integer"
        }
    ]
}
```

### POST `/api/v1/admin/safety/unlock-account`

Разблокировка аккаунта пользователя.

**Request Body:**
```json
{
    "user_id": "uuid",
    "reason": "string"
}
```

## 📊 Статистика

### GET `/api/v1/admin/stats/overview`

Общая статистика системы.

**Response:**
```json
{
    "users": {
        "total": "integer",
        "active": "integer",
        "inactive": "integer",
        "new_today": "integer",
        "new_this_week": "integer",
        "new_this_month": "integer"
    },
    "auth": {
        "logins_today": "integer",
        "logins_this_week": "integer",
        "failed_attempts_today": "integer",
        "blocked_accounts": "integer"
    },
    "security": {
        "blocked_ips": "integer",
        "suspicious_activities": "integer"
    }
}
```

### GET `/api/v1/admin/stats/users/activity`

Статистика активности пользователей за период.

**Query Parameters:**
- `period`: daily/weekly/monthly
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD

### GET `/api/v1/admin/stats/auth/failures`

Статистика неудачных попыток входа.

## 💚 Здоровье системы

### GET `/health`

Проверка состояния сервиса.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "datetime",
    "version": "string",
    "database": "connected",
    "cache": "connected"
}
```

## 🔍 Общие принципы

### Аутентификация

Большинство endpoints требуют Bearer токен в заголовке:
```
Authorization: Bearer {access_token}
```

### Пагинация

Список endpoints поддерживают пагинацию:
- `page`: Номер страницы (начинается с 1)
- `size`: Количество элементов на странице

### Обработка ошибок

Все ошибки возвращаются в стандартном формате:
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {}
    }
}
```

### Коды ошибок

- `400`: Bad Request - неверный запрос
- `401`: Unauthorized - не авторизован
- `403`: Forbidden - нет прав доступа
- `404`: Not Found - ресурс не найден
- `422`: Validation Error - ошибка валидации
- `423`: Account Locked - аккаунт заблокирован
- `429`: Too Many Requests - превышен лимит запросов
- `500`: Internal Server Error - внутренняя ошибка сервера

## 📝 Схемы данных

### User Schema
```json
{
    "id": "uuid",
    "user_name": "string",
    "email": "string",
    "full_name": "string",
    "bio": "string",
    "email_verified": "boolean",
    "is_active": "boolean",
    "last_login": "datetime",
    "login_count": "integer",
    "roles": ["Role"],
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### Role Schema
```json
{
    "id": "uuid",
    "name": "string",
    "description": "string",
    "permissions": "integer",
    "user_count": "integer",
    "created_at": "datetime"
}
```

### Login Request
```json
{
    "user_name": "string",
    "password": "string"
}
```

### Register Request
```json
{
    "user_name": "string",
    "email": "string",
    "password": "string",
    "full_name": "string",
    "bio": "string"
}
```

## 🚀 Быстрые примеры

### Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "user_name": "john_doe",
       "email": "john@example.com",
       "password": "secure_password",
       "full_name": "John Doe"
     }'
```

### Аутентификация
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "user_name": "john_doe",
       "password": "secure_password"
     }'
```

### Получение профиля
```bash
curl -X GET "http://localhost:8000/api/v1/users/profile" \
     -H "Authorization: Bearer {access_token}"
```

### Административная статистика
```bash
curl -X GET "http://localhost:8000/api/v1/admin/stats/overview" \
     -H "Authorization: Bearer {admin_access_token}"
```

---

💡 **Совет**: Используйте интерактивную документацию Swagger по адресу `http://localhost:8000/docs` для тестирования API в браузере.