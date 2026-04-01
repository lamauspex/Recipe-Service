""" Dependencies для recipe_service """

from fastapi import Depends, HTTPException, status, Header
from typing import Optional

from backend.service_recipe.src.infrastructure.grpc_client import (
    UserServiceClient,
    get_user_service_client
)


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
