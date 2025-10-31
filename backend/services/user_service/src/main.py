"""
Точка входа для user-service
Автономная реализация без зависимостей от общих модулей
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as uvi_run
from contextlib import asynccontextmanager
import os

from backend.services.user_service.src.api.routes import router
from backend.services.user_service.src.database.connection import init_db
from backend.services.user_service.src.middleware.exception_handler import (
    setup_exception_handlers
)


# Получаем настройки из переменных окружения
SERVICE_NAME = "user-service"
PORT = int(os.getenv("USER_SERVICE_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan для управления состоянием приложения"""
    # Код при запуске приложения
    init_db()
    print(f"{SERVICE_NAME} started on port {PORT}")
    yield
    # Код при остановке приложения
    print(f"{SERVICE_NAME} shutting down.")


app = FastAPI(
    title="User Service API",
    description="Сервис управления пользователями",
    version="1.0.0",
    lifespan=lifespan,
    debug=DEBUG
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка обработчиков ошибок
setup_exception_handlers(app)

# Подключение роутеров
app.include_router(router)


@app.get("/")
async def root():
    """Корневой эндпоинт с информацией о сервисе"""
    return {
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "status": "running"
    }


if __name__ == "__main__":
    uvi_run(app, host="0.0.0.0", port=PORT)
