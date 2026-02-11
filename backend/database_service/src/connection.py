"""
Подключение к базе данных для user-service
Использует общую базу данных со всеми сервисами
Теперь без глобальных переменных - управляется через DI контейнер
"""

from typing import Generator

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

from backend.database_service.src.config.database import DataBaseConfig
from backend.shared.models.base_models import Base


def create_engine_for_service(database_config_instance):
    """
    Создание движка базы данных для user-service
    Использует ОДНУ общую базу данных со всеми сервисами
    """
    # Для тестового окружения используем SQLite в памяти
    if database_config_instance.TESTING:

        database_url = database_config_instance.get_database_url()
        engine_kwargs = {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
            "echo": False  # Отключаем SQL логирование даже в тестах
        }
    else:
        # Для продакшена - PostgreSQL с пулом соединений
        database_url = database_config_instance.get_database_url()
        engine_kwargs = {
            "echo": False,  # Отключаем SQL логирование
            "pool_pre_ping": True,
            "pool_size": 10,
            "max_overflow": 20,
            "connect_args": {
                "client_encoding": "utf8",
                "options": "-c client_encoding=utf8"
            }
        }

    return create_engine(
        database_url,
        **engine_kwargs
    )


class DatabaseManager:
    """
    Менеджер базы данных для user-service
    Инкапсулирует всю логику работы с БД в одном классе
    Теперь не содержит глобальных переменных
    """

    def __init__(self, database_config_instance):
        """
        Инициализация менеджера БД
        """
        self.config = database_config_instance
        self.engine = create_engine_for_service(database_config_instance)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_db(self) -> Generator[Session, None, None]:
        """
        Dependency function для FastAPI - предоставляет сессию БД
        Используется в эндпоинтах
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @contextmanager
    def get_db_context(self) -> Generator[Session, None, None]:
        """
        Контекстный менеджер для работы с сессией базы данных
        Автоматически коммитит изменения и откатывает при ошибках

        Пример:
            from user_service.database import database

            with database.get_db_context() as db:
                user = User(name="test")
                db.add(user)
                # автоматически коммитится при выходе из контекста
        """
        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def init_db(self) -> None:
        """
        Инициализация базы данных - создание таблиц user-service
        Создает только таблицы, относящиеся к user-service
        """
        # Тестируем подключение
        if not self.test_connection():
            raise Exception("Cannot connect to database")

        # Создаем таблицы только для user-service
        Base.metadata.create_all(bind=self.engine)

    def test_connection(self) -> bool:
        """
        Тестирование подключения к базе данных
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def get_db_session(self) -> Session:
        """
        Получение сессии базы данных
        (для использования вне контекстного менеджера)
        """
        return self.SessionLocal()

    def close_db_connection(self, db: Session) -> None:
        """
        Закрытие соединения с базой данных
        """
        db.close()

    def recreate_database(self) -> None:
        """
        Пересоздание базы данных (для тестов и разработки)
        УДАЛЯЕТ ВСЕ ДАННЫЕ!
        """
        if self.config.environment not in ["test", "development"]:
            raise Exception(
                "Cannot recreate database in production environment"
            )

        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)


config = DataBaseConfig()
database = DatabaseManager(config)
