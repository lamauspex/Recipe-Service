"""
Подключение к базе данных для user-service
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import psycopg2

from backend.settings import settings
from backend.services.user_service.src.models import Base


# Создание движка SQLAlchemy с правильным драйвером
DATABASE_URL = (
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)


# Создание движка SQLAlchemy с дополнительными параметрами для кодировки
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Включаем логирование для отладки
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={
        "client_encoding": "utf8",
        "options": "-c client_encoding=utf8"
    }
)

# Создание фабрики сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function для FastAPI - предоставляет сессию БД
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Контекстный менеджер для работы с сессией базы данных
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def test_connection() -> bool:
    """
    Тестирование подключения к базе данных
    """
    try:
        print("Testing database connection...")
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            client_encoding='utf8'
        )
        conn.close()
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


def init_db() -> None:
    """
    Инициализация базы данных - создание всех таблиц
    """
    try:
        print("Initializing database...")

        # Сначала тестируем подключение
        if not test_connection():
            raise Exception("Cannot connect to database")

        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise


def get_db_session() -> Session:
    """
    Получение сессии базы данных
    (для использования вне контекстного менеджера)
    """
    return SessionLocal()


def close_db_connection(db: Session) -> None:
    """
    Закрытие соединения с базой данных
    """
    db.close()
