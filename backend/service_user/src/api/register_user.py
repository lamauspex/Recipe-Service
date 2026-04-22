""" API Routers Register """

from fastapi import APIRouter, Depends, status

from backend.service_user.src.infrastructure.dependencies import (
    get_register_service
)
from backend.service_user.src.service import RegisterService
from backend.service_user.src.schemas.register import (
    UserCreate,
    UserResponseDTO
)


# Создаем router
router = APIRouter(
    prefix="/register",
    tags=["Register"]
)


@router.post(
    "/register",
    summary="Регистрация пользователя",
    description="Создание нового пользователя",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Пользователь с таким email/именем существует"},
        422: {"description": "Ошибка валидации данных"}
    }
)
async def register_user(
    register_data: UserCreate,
    register_service: RegisterService = Depends(get_register_service)
) -> UserResponseDTO:
    """
    Регистрация пользователя
    Сервис возвращает готовый UserResponseDTO
    """

    return register_service.register_user(register_data)


# @router.get(
#     "/{user_id}/profile",
#     summary="Получение профиля пользователя",
#     description="Получение данных профиля пользователя по ID.",
#     response_model=UserResponseDTO,
#     status_code=status.HTTP_200_OK,
#     responses={
#         404: {"description": "Пользователь не найден"}
#     }
# )
# async def get_profile(
#     user_id: str
# ) -> UserResponseDTO:
#     """
#     Получение профиля пользователя

#     - **user_id**: ID пользователя

#     Возвращает публичные данные пользователя
#     """
#     # TODO: Реализовать получение профиля
#     raise NotImplementedError("Endpoint not implemented yet")


# @router.put(
#     "/profile",
#     summary="Обновление профиля",
#     description="Обновление данных текущего пользователя.",
#     response_model=UserResponseDTO,
#     status_code=status.HTTP_200_OK
# )
# async def update_profile():
#     """
#     Обновление профиля текущего пользователя

#     Требует аутентификации (JWT токен)
#     """
#     # TODO: Реализовать обновление профиля
#     raise NotImplementedError("Endpoint not implemented yet")
