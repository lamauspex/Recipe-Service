"""
Подключение к базе данных для user-service
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os

from backend.services.user_service.src.database.connection import Base

# Получение настроек из окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/user_service_db"
)

# Создание движка SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Создание фабрики сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Контекстный менеджер для работы с сессией базы данных"""
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
    """Инициализация базы данных - создание всех таблиц"""
    Base.metadata.create_all(bind=engine)


def get_db_session() -> Session:
    """Получение сессии базы данных
    (для использования вне контекстного менеджера)"""
    return SessionLocal()


def close_db_connection(db: Session) -> None:
    """Закрытие соединения с базой данных"""
    db.close()
