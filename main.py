"""
Точка входа приложения
Использует общую конфигурацию из backend.shared
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as uvi_run
from contextlib import asynccontextmanager

from backend.services.user_service.src.api.routes import router
from backend.services.user_service.src.database.connection import init_db
from backend.services.user_service.src.middleware.exception_handler import (
    setup_exception_handlers
)
from backend.shared.config import get_settings

# Получаем настройки
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan для управления состоянием приложения"""
    # Код при запуске приложения
    init_db()
    print(f"{settings.SERVICE_NAME} started on port {settings.SERVICE_PORT}")
    yield
    # Код при остановке приложения
    print(f"{settings.SERVICE_NAME} shutting down.")


app = FastAPI(
    title="User Service API",
    description="Сервис управления пользователями",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "status": "running"
    }


if __name__ == "__main__":
    uvi_run(app, host="0.0.0.0", port=int(settings.SERVICE_PORT))
