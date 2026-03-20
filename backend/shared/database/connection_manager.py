"""
Менеджер соединений с базой данных
Отвечает только за создание и управление engine
"""

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.engine import Engine


class ConnectionManager:
    """
    Управляет соединениями с БД
    SRP: только соединения, не управляет сессиями
    """

    def __init__(self, database_config):
        """
        Инициализация менеджера соединений

        Args:
            database_config: Конфигурация БД
        """
        self.config = database_config
        self._engine = self._create_engine()

    def _create_engine(self) -> Engine:
        """
        Создает engine с настройками под окружение

        Returns:
            SQLAlchemy Engine
        """
        if self.config.TESTING:
            return create_engine(
                self.config.get_database_url(),
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )

        return create_engine(
            self.config.get_database_url(),
            echo=False,
            pool_pre_ping=True,
            pool_size=self.config.POOL_SIZE,
            max_overflow=self.config.MAX_OVERFLOW,
            connect_args={
                "client_encoding": "utf8",
                "options": "-c client_encoding=utf8"
            }
        )

    @property
    def engine(self) -> Engine:
        """
        Получить engine

        Returns:
            SQLAlchemy Engine
        """
        return self._engine

    def test_connection(self) -> bool:
        """
        Проверка подключения к БД

        Returns:
            True если подключение успешно, иначе False
        """
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def close(self) -> None:
        """
        Закрыть engine (для graceful shutdown)
        """
        if self._engine:
            self._engine.dispose()
