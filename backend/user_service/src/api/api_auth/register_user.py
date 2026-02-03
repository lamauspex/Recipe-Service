
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database_service import database
from user_service.schemas import UserCreate, UserResponse
from user_service.services import RegisterService
from user_service.repository import UserRepository


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
