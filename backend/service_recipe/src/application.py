"""
FastAPI application factory

Создаёт и настраивает FastAPI приложение
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from backend.service_recipe.src.lifespan import lifespan
from backend.service_recipe.src.infrastructure import container
from backend.shared.logging.middleware import LoggingMiddleware
from backend.service_recipe.src.api import api_router


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение
    """

    api_config = container.api_config()
    cors_config = container.cors_config()

    app = FastAPI(
        title=api_config.API_TITLE,
        description=api_config.API_DESCRIPTION,
        version=api_config.API_VERSION,
        docs_url="/docs" if api_config.DEBUG else None,
        redoc_url="/redoc" if api_config.DEBUG else None,
        lifespan=lifespan
    )

    # ✅ CORS ПЕРВЫЙ (важно для preflight запросов!)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.CORS_ORIGINS,
        allow_credentials=cors_config.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключаем middleware логирования
    app.add_middleware(
        LoggingMiddleware,
        service_name="Recipe_Service"
    )

    # Настроить security scheme для Swagger
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )

        # Добавить Bearer Auth scheme
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Подключаем API роутеры
    app.include_router(api_router)

    return app
