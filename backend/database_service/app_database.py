"""
Главный файл приложения Database Service
"""

from fastapi import FastAPI
from .connection import database
from .src.lifespan import lifespan


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение для Database Service
    """
    app = FastAPI(
        title="Database Service API",
        description="Сервис управления базой данных",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    @app.get("/health")
    async def health_check():
        """Проверка здоровья сервиса базы данных"""
        try:
            if database.test_connection():
                return {"status": "healthy", "service": "database_service"}
            else:
                return {"status": "unhealthy", "service": "database_service", "error": "Database connection failed"}
        except Exception as e:
            return {"status": "unhealthy", "service": "database_service", "error": str(e)}

    @app.get("/")
    async def root():
        """Корневой endpoint"""
        return {"message": "Database Service is running"}

    return app


# Приложение по умолчанию
app_database = create_app()
