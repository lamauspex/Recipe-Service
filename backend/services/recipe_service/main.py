"""
Точка входа для recipe-service
Автономная реализация без зависимостей от общих модулей
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as uvi_run
from contextlib import asynccontextmanager
import os

from backend.services.recipe_service.src.api.recipe_router import router
from backend.services.recipe_service.src.database.connection import init_db, get_db_session_factory
from backend.services.recipe_service.src.events.publishers import recipe_event_publisher
from backend.services.recipe_service.src.events.consumers import start_recipe_consumers, stop_recipe_consumers


# Получаем настройки из переменных окружения
SERVICE_NAME = "recipe-service"
PORT = int(os.getenv("RECIPE_SERVICE_PORT"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT")
CORS_ORIGINS = os.getenv("CORS_ORIGINS").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan для управления состоянием приложения"""
    # Инициализация базы данных
    init_db()

    # Подключение к RabbitMQ
    try:
        await recipe_event_publisher.connect()
        print("RabbitMQ connected for recipe-service")

        # Запуск потребителей
        db_session_factory = get_db_session_factory()
        await start_recipe_consumers(db_session_factory)
        print("Recipe service consumers started")

    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        # Продолжаем работу без RabbitMQ для разработки

    print(f"{SERVICE_NAME} started on port {PORT}")
    yield

    # Очистка при остановке
    try:
        await stop_recipe_consumers()
        await recipe_event_publisher.disconnect()
        print("RabbitMQ disconnected for recipe-service")
    except Exception as e:
        print(f"Error disconnecting from RabbitMQ: {e}")

    print(f"{SERVICE_NAME} shutting down.")


app = FastAPI(
    title="Recipe Service API",
    description="Сервис управления рецептами",
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
