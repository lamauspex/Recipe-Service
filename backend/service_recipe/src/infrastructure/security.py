"""
Security configuration for Recipe Service

Использует HTTP Bearer scheme для JWT токенов

Принципы:
- HTTP Bearer автоматически добавляется в OpenAPI schema
- Swagger UI показывает простое поле для Bearer токена
- Кнопка "Authorize" реально передаёт токен в запросах
"""

from fastapi.security import HTTPBearer


# Создаём HTTP Bearer scheme
# Просто проверяет заголовок Authorization: Bearer <token>
oauth2_scheme = HTTPBearer(
    description="Введите JWT токен для авторизации. Формат: Bearer <token>"
)
