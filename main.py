"""
Главный файл запуска всех сервисов
"""

import uvicorn

from app_service import app_service

if __name__ == "__main__":

    uvicorn.run(
        app_service
    )
