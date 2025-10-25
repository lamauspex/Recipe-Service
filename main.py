from fastapi import FastAPI
from uvicorn import run as uvi_run

from backend.services.user_service.src.api.routes import router
from backend.services.user_service.src.middleware.exception_handler import (
    setup_exception_handlers
)
from backend.settings import settings

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    print("Application started.")

setup_exception_handlers(app)
app.include_router(router)

if __name__ == "__main__":
    uvi_run(app, host="0.0.0.0", port=int(settings.SERVICE_PORT))
