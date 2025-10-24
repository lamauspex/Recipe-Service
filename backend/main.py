"""
Запуск всех серверов
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.services.user_service.src.api.routes import router
from backend.services.user_service.src.middleware.exception_handler import (
    setup_exception_handlers
)
from backend.services.user_service.src.database.connection import init_db

app = FastAPI(
    title="User Service",
    description="API для управления пользователями платформы рецептов",
    version="1.0.0"
)


# Инициализация базы данных при старте
@app.on_event("startup")
async def startup_event():
    """Инициализация базы данных при запуске сервиса"""
    init_db()


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение обработчиков исключений
setup_exception_handlers(app)

# Подключение роутеров
app.include_router(router, prefix="/api/v1/users", tags=["users"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "User Service is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "service": "User Service",
        "status": "healthy",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
