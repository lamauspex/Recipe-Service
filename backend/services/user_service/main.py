"""
Точка входа для user-service
Автономная реализация без зависимостей от общих модулей
"""

from dotenv import load_dotenv
from contextlib import asynccontextmanager
from uvicorn import run as uvi_run
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from backend.services.user_service.src.events.publishers import (
    user_event_publisher)
from backend.services.user_service.src.api.routes import router
from backend.services.user_service.src.database.connection import init_db
from backend.services.user_service.src.middleware.exception_handler import (
    setup_exception_handlers
)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))


# Загружаем переменные окружения из .env файла
load_dotenv()


# Получаем настройки
SERVICE_NAME = "user-service"
PORT = int(os.getenv("USER_SERVICE_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan для управления состоянием приложения"""
    # Инициализация базы данных
    init_db()

    # Подключение к RabbitMQ
    try:
        await user_event_publisher.connect()
        print(f"RabbitMQ connected for {SERVICE_NAME}")
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        print(f"{SERVICE_NAME} will work without RabbitMQ")

    print(f"{SERVICE_NAME} started on port {PORT}")
    yield

    # Очистка при остановке
    try:
        await user_event_publisher.disconnect()
        print(f"RabbitMQ disconnected for {SERVICE_NAME}")
    except Exception as e:
        print(f"Error disconnecting from RabbitMQ: {e}")

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
