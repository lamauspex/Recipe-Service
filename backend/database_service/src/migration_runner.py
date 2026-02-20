"""
Запуск миграций Alembic

Обёртка над Alembic для программного управления миграциями.
Используется в lifespan для авто-миграций и для ручного управления.

"""

from alembic.config import Config
from alembic import command


class MigrationRunner:
    """
    Attributes:
        database_url: URL подключения к базе данных
        migrations_path: Путь к директории с миграциями
        alembic_cfg: Конфигурация Alembic

    Example:
        runner = MigrationRunner(
            database_url="postgresql://user:pass@localhost/db",
            migrations_path="./migrations"
        )
        runner.upgrade("head")
    """

    def __init__(self, database_url: str, migrations_path: str):
        """
        Инициализация runner'а миграций

        Args:
            database_url: URL подключения к базе данных (формат SQLAlchemy)
                         Пример: "postgresql://user:pass@localhost:5432/db"
            migrations_path: Путь к директории с миграциями Alembic
                           Обычно "./migrations" или абсолютный путь

        Raises:
            FileNotFoundError: Если директория миграций не существует
        """
        self.database_url = database_url
        self.migrations_path = migrations_path
        self.alembic_cfg = Config()

    def upgrade(self, revision: str = "head") -> None:
        """
        Применить миграции до указанной версии

        Args:
            revision: Целевая версия миграции
                     - "head": до последней версии (по умолчанию)
                     - "+1": на одну версию вперёд
                     - "rev_id": конкретная версия (например, "1a2b3c4d")

        Example:
            runner.upgrade()  # до последней версии
            runner.upgrade("+1")  # на одну версию вперёд
            runner.upgrade("1a2b3c4d")  # до конкретной версии

        Raises:
            alembic.util.CommandError: При ошибке миграции
        """
        self._configure()
        command.upgrade(self.alembic_cfg, revision)

    def downgrade(self, revision: str = "-1") -> None:
        """
        Откатить миграции до указанной версии

        Args:
            revision: Целевая версия для отката
                     - "-1": на одну версию назад (по умолчанию)
                     - "base": до начального состояния (все миграции)
                     - "rev_id": конкретная версия

        Example:
            runner.downgrade()  # на одну версию назад
            runner.downgrade("base")  # до начального состояния
            runner.downgrade("1a2b3c4d")  # до конкретной версии

        Raises:
            alembic.util.CommandError: При ошибке отката
        """
        self._configure()
        command.downgrade(self.alembic_cfg, revision)

    def _configure(self) -> None:
        """
        Настройка конфигурации Alembic

        Устанавливает URL базы данных и путь к директории миграций.
        Вызывается автоматически перед каждой командой.

        Note:
            Конфигурация пересоздаётся перед каждой командой,
            чтобы учитывать возможные изменения в database_url
        """
        self.alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)
        self.alembic_cfg.set_main_option(
            "script_location",
            self.migrations_path
        )

    def current(self) -> str:
        """
        Получить текущую версию миграции

        Returns:
            Строка с текущей версией миграции или пустая строка,
            если миграции не применены

        Example:
            current = runner.current()
            print(f"Текущая версия: {current}")

        Returns:
            str: Текущая версия (например, "1a2b3c4d") или ""
        """
        self._configure()
        return command.current(self.alembic_cfg)
