"""
Dependencies для recipe_service

Принципы:
- Единая точка входа для всех зависимостей
- Dependency Injection через FastAPI Depends
- Сессия БД создаётся на каждый запрос и закрывается автоматически
"""

from fastapi import Depends, HTTPException, status, Header
from typing import Optional
# from sqlalchemy.orm import Session

from backend.service_recipe.src.infrastructure.container import container
from backend.service_recipe.src.infrastructure.grpc_client import (
    UserServiceClient,
    get_user_service_client
)
from backend.service_recipe.src.service.message_broker import MessagePublisher


# ==========================================
# ПОДКЛЮЧЕНИЕ К БД
# ==========================================

def get_db():
    """
    Dependency для получения сессии БД
    """
    session_manager = container.session_manager()
    session = session_manager.SessionLocal()

    try:
        yield session
    finally:
        session.close()


# ==========================================
# ПОДКЛЮЧЕНИЕ К USER_SERVICE
# ==========================================

async def get_current_user(
    authorization: Optional[str] = Header(None),
    user_client: UserServiceClient = Depends(get_user_service_client)
) -> dict:
    """
    Dependency для получения текущего авторизованного пользователя

    Проверяет JWT токен через gRPC вызов к user_service
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    # Извлекаем токен из заголовка "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    token = parts[1]

    # Валидируем токен через gRPC
    result = await user_client.validate_token(token)

    if not result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Invalid token")
        )

    return {
        "user_id": result["user_id"],
        "email": result["email"]
    }


# ==========================================
# СЕРВИСЫ
# ==========================================
# Глобальный экземпляр
# Publisher для отправки событий в RabbitMQ
_publisher: Optional[MessagePublisher] = None


def get_message_publisher() -> MessagePublisher:
    """Dependency для получения publisher"""
    global _publisher
    rebbit_config = container.rebbit_config()

    if _publisher is None:
        _publisher = MessagePublisher(rebbit_config.RABBITMQ_URL)

    return _publisher

# ==========================================
# РЕПОЗИТОРИИ
# ==========================================
