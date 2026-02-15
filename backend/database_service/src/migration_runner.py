"""
Запуск миграций Alembic
"""

from alembic.config import Config
from alembic import command


class MigrationRunner:
    """Запускает миграции базы данных"""

    def __init__(self, database_url: str, migrations_path: str):
        self.database_url = database_url
        self.migrations_path = migrations_path
        self.alembic_cfg = Config()

    def upgrade(self, revision: str = "head") -> None:
        """Применить миграции"""
        self._configure()
        command.upgrade(self.alembic_cfg, revision)

    def downgrade(self, revision: str = "-1") -> None:
        """Откатить миграции"""
        self._configure()
        command.downgrade(self.alembic_cfg, revision)

    def _configure(self) -> None:
        """Настройка Alembic"""
        self.alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)
        self.alembic_cfg.set_main_option(
            "script_location",
            self.migrations_path
        )

    def current(self) -> str:
        """Текущая версия миграции"""
        self._configure()
        return command.current(self.alembic_cfg)
