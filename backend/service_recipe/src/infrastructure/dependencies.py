"""
Dependencies для recipe_service

Принципы:
- Единая точка входа для всех зависимостей
- Dependency Injection через FastAPI Depends
- Сессия БД создаётся на каждый запрос и закрывается автоматически
"""


from typing import Optional

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from backend.service_recipe.src.infrastructure import (
    container
)
from backend.service_recipe.src.infrastructure.grpc.client import (
    UserServiceClient)
from backend.service_recipe.src.repositories import SQLRecipeRepository
from backend.service_recipe.src.service import (
    MessagePublisher,
    RecipeService
)


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
# АВТОРИЗАЦИЯ
# ==========================================

def get_user_service_client() -> UserServiceClient:
    """Получение gRPC клиента из контейнера"""
    return container.user_service_client()


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
# MESSAGE PUBLISHER
# ==========================================

# Провайдер создаётся через DI контейнер
def get_message_publisher() -> MessagePublisher:
    """
    Получение publisher из DI контейнера.
    Создаётся один раз за lifecycle приложения.
    """
    return container.message_publisher()


# ==========================================
# РЕПОЗИТОРИИ
# ==========================================

def get_recipe_repository(
    db: Session = Depends(get_db)
) -> SQLRecipeRepository:
    """Dependency для получения репозитория рецептов"""
    return SQLRecipeRepository(db)


# ==========================================
# СЕРВИСЫ
# ==========================================

def get_recipe_service(
    recipe_repo: SQLRecipeRepository = Depends(get_recipe_repository)
) -> RecipeService:
    """ Dependency для получения сервиса рецептов """
    return RecipeService(recipe_repo=recipe_repo)
