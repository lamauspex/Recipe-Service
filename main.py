"""
Главный файл запуска User Service

"""

import uvicorn

from backend.user_service.app_users import app_users

if __name__ == "__main__":

    uvicorn.run(
        app_users
    )
