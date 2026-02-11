from fastapi import APIRouter
from backend.database_service.src.container import container

router = APIRouter()


@router.post("/create")
async def create_schema():
    """Создать все таблицы"""
    manager = container.database_manager()
    manager.init_db()
    return {"status": "created"}


@router.post("/drop")
async def drop_schema():
    """Удалить все таблицы"""
    manager = container.database_manager()
    manager.recreate_database()
    return {"status": "dropped"}
