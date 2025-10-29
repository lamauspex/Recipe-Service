"""
Базовое подключение к базе данных для всех микросервисов
Поддерживает контейнеризацию и микросервисную архитектуру
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import os

from backend.shared.config import get_settings
from backend.services.user_service.src.models import BaseModel as UserBase

# Базовый класс для всех моделей
Base = declarative_base()


def create_database_engine():
    """
    Создание движка базы данных с поддержкой разных окружений
    """
    settings = get_settings()

    # Формирование DSN для PostgreSQL
    database_url = (
        f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )

    # Параметры движка
    engine_kwargs = {
        "echo": settings.DEBUG,  # Логирование SQL в режиме отладки
        "pool_pre_ping": True,   # Проверка соединения перед использованием
        "pool_size": 10,
        "max_overflow": 20,
        "connect_args": {
            "client_encoding": "utf8",
            "options": "-c client_encoding=utf8"
        }
    }

    # Для тестового окружения используем SQLite в памяти
    if os.getenv("TESTING"):
        database_url = "sqlite:///:memory:"
        engine_kwargs.update({
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool
        })

    return create_engine(database_url, **engine_kwargs)


# Глобальный движок базы данных
engine = create_database_engine()

# Фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function для FastAPI - предоставляет сессию БД
    Используется в эндпоинтах
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
    Автоматически коммитит изменения и откатывает при ошибках
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


def init_db() -> None:
    """
    Инициализация базы данных - создание всех таблиц
    Должна вызываться каждым сервисом для своих моделей
    """
    try:
        # Создаем таблицы
        UserBase.metadata.create_all(bind=engine)
        print("Database tables created successfully.")

    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise


def test_connection() -> bool:
    """
    Тестирование подключения к базе данных
    """
    try:
        with get_db_context() as db:
            db.execute(text("SELECT 1"))
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


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


def recreate_database() -> None:
    """
    Пересоздание базы данных (для тестов и разработки)
    УДАЛЯЕТ ВСЕ ДАННЫЕ!
    """
    if os.getenv("ENVIRONMENT") not in ["test", "development"]:
        raise RuntimeError(
            "Cannot recreate database in production environment")

    UserBase.metadata.drop_all(bind=engine)
    UserBase.metadata.create_all(bind=engine)
    print("Database recreated successfully.")
