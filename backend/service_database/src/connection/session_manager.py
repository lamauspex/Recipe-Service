"""
Менеджер базы данных — провайдер соединений и сессий
НЕ управляет схемой данных (это делают миграции)
"""

from typing import Generator
from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine


class SessionManager:
    """
    Управляет сессиями БД
    SRP: только сессии, не управляет соединениями
    DIP: зависит от абстракции Engine, не от конкретной реализации
    """

    def __init__(self, engine: Engine):
        """
        Инициализация менеджера сессий

        Args:
            engine: SQLAlchemy Engine (получается из ConnectionManager)
        """
        self._engine = engine
        self._SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )

    @property
    def SessionLocal(self) -> sessionmaker:
        """
        Получить factory для создания сессий

        Returns:
            SQLAlchemy sessionmaker
        """
        return self._SessionLocal

    def get_db(self) -> Generator[Session, None, None]:
        """
        FastAPI dependency — сессия с авто-закрытием

        Yields:
            SQLAlchemy Session
        """
        db = self._SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @contextmanager
    def get_db_context(
        self,
        auto_commit: bool = True
    ) -> Generator[Session, None, None]:
        """
        Контекстный менеджер для работы с сессией

        Args:
            auto_commit: True — коммит при успехе, rollback при ошибке
                        False — явный контроль коммита

        Yields:
            SQLAlchemy Session

        Example:
            with session_manager.get_db_context() as db:
                user = db.query(User).first()
                # auto_commit=True — коммит при выходе из контекста

            with session_manager.get_db_context(auto_commit=False) as db:
                user = db.query(User).first()
                db.commit()  # явный коммит
        """
        db = self._SessionLocal()
        try:
            yield db
            if auto_commit:
                db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
