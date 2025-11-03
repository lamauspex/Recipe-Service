"""
Подключение к базе данных для user-service
Использует общую базу данных со всеми сервисами
"""

from backend.services.user_service.models.base_models import Base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


def create_engine_for_service():
    """
    Создание движка базы данных для user-service
    Использует ОДНУ общую базу данных со всеми сервисами
    """
    # Получаем настройки из переменных окружения
    db_user = os.getenv("DB_USER")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_pass = os.getenv("DB_PASSWORD")

    # Формируем DSN
    database_url = (
        f"postgresql+psycopg2://{db_user}:{db_pass}"
        f"@{db_host}:{db_port}/{db_name}"
    )

    # Параметры движка
    engine_kwargs = {
        "echo": os.getenv("DEBUG", "False").lower() == "true",
        "pool_pre_ping": True,
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
engine = create_engine_for_service()

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
    Инициализация базы данных - создание таблиц user-service
    Создает только таблицы, относящиеся к user-service
    """
    try:
        print("Initializing user-service database tables...")

        # Тестируем подключение
        if not test_connection():
            raise Exception("Cannot connect to database")

        # Создаем таблицы только для user-service
        Base.metadata.create_all(bind=engine)
        print("User service database tables created successfully.")

    except Exception as e:
        print(f"Error creating user service database tables: {e}")
        raise


def test_connection() -> bool:
    """
    Тестирование подключения к базе данных
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection for user-service successful!")
        return True
    except Exception as e:
        print(f"Database connection for user-service failed: {e}")
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
        raise Exception("Cannot recreate database in production environment")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database for user-service recreated successfully.")
