
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database_service.connection import database
from backend.user_service.src.schemas import UserCreate, UserResponse
from backend.user_service.src.services import RegisterService
from backend.user_service.src.repository import UserRepository


# Создаем router
router = APIRouter(
    prefix="/auth_users",
    tags=["Auth_Service"]
)


@router.post(
    "/register",
    summary="Регистрация пользователя",
    response_model=UserResponse
)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(database.get_db)
):
    user_repo = UserRepository(db)
    user_service = RegisterService(user_repo)

    return user_service.register_user(user_data)
