"""
Подключение к базе данных для user-service
Обертка над общим подключением из backend.database
"""

from sqlalchemy import create_engine

from backend.shared.config import get_settings
from backend.database.models import BaseModel

# Используем общее подключение из базового модуля
from backend.database.connection import (
    get_db as base_get_db,
    get_db_context as base_get_db_context,
    get_db_session as base_get_db_session,
    close_db_connection as base_close_db_connection,
    test_connection as base_test_connection,
    SessionLocal as base_SessionLocal
)

# Получаем настройки
settings = get_settings()

# Простые альтернативы для обратной совместимости
get_db = base_get_db
get_db_context = base_get_db_context
get_db_session = base_get_db_session
close_db_connection = base_close_db_connection
test_connection = base_test_connection
SessionLocal = base_SessionLocal

# Создание движка SQLAlchemy с правильным драйвером
DATABASE_URL = (
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# Создание движка SQLAlchemy с дополнительными параметрами для кодировки
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Вкл логирование для отладки
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={
        "client_encoding": "utf8",
        "options": "-c client_encoding=utf8"
    }
)


def init_db() -> None:
    """
    Инициализация базы данных - создание таблиц user-service
    """
    try:
        print("Initializing user-service database tables...")

        # Тестируем подключение
        if not test_connection():
            raise Exception("Cannot connect to database")

        # Создаем таблицы только для user-service
        BaseModel.metadata.create_all(bind=engine)
        print("User service database tables created successfully.")

    except Exception as e:
        print(f"Error creating user service database tables: {e}")
        raise
