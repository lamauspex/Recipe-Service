from fastapi import FastAPI
from uvicorn import run as uvi_run
from contextlib import asynccontextmanager

from backend.services.user_service.src.api.routes import router
from backend.services.user_service.src.database.connection import init_db
from backend.services.user_service.src.middleware.exception_handler import (
    setup_exception_handlers
)
from backend.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код при запуске приложения
    init_db()
    print("Application started.")
    yield
    # Код при остановке приложения (если нужен)
    print("Application shutting down.")


app = FastAPI(
    title="User Service API",
    description="Сервис управления пользователями",
    version="1.0.0",
    lifespan=lifespan
)


setup_exception_handlers(app)
app.include_router(router)

if __name__ == "__main__":
    uvi_run(app, host="0.0.0.0", port=int(settings.SERVICE_PORT))
