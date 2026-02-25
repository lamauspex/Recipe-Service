"""
Alembic Environment Configuration

Этот файл конфигурирует Alembic для работы с SQLAlchemy моделями.
Alembic использует его для генерации и применения миграций.

Настройка:
1. Импортирует все модели, которые должны участвовать в миграциях
2. Настраивает подключение к БД через DataBaseConfig
3. Определяет режим работы (online/offline)

ВАЖНО: Все модели, для которых нужны миграции, должны:
- Импортироваться в этом файле
- Наследоваться от Base (из backend.shared.models.base.base_models)
- Быть доступны в metadata Base

Пример добавления новой модели:
    from backend.user_service.models import User  # добавить импорт
    # Модель User автоматически попадёт в Base.metadata
"""

from alembic import context
from sqlalchemy import pool
from sqlalchemy import engine_from_config
from backend.service_database.src.config.database import DataBaseConfig
from backend.shared.models.base.base_models import Base
from logging.config import fileConfig
import os
import sys
from pathlib import Path

# Добавляем путь к backend в sys.path для импортов моделей
backend_path = Path(__file__).parent.parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# ==========================================
# КОНФИГУРАЦИЯ ALEMBIC
# ==========================================

# Получаем конфигурацию Alembic из alembic.ini
config = context.config

# Настраиваем логирование если есть файл конфигурации
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ==========================================
# НАСТРОЙКА ПОДКЛЮЧЕНИЯ К БД
# ==========================================

# Получаем конфигурацию БД из переменных окружения
database_config = DataBaseConfig()

# Получаем URL базы данных
# Для тестов (TESTING=true) будет использоваться SQLite in-memory
# Для production - PostgreSQL из переменных окружения
database_url = database_config.get_database_url()
os.environ["DATABASE_URL"] = database_url

# ==========================================
# МЕТАДАННЫЕ МОДЕЛЕЙ
# ==========================================

# Base.metadata содержит все модели, которые наследуются от Base
# При добавлении новых моделей просто импортируйте их выше
# и они автоматически попадут в metadata

# Пример импорта моделей из других сервисов:
# from backend.user_service.models import User
# from backend.auth_service.models import Role, Permission

target_metadata = Base.metadata

# ==========================================
# ФУНКЦИИ ЗАПУСКА МИГРАЦИЙ
# ==========================================


def run_migrations_offline() -> None:
    """
    Запуск миграций в 'offline' режиме

    В этом режиме не создаётся реальное подключение к БД.
    Генерируется SQL скрипт, который можно выполнить вручную.

    Используется когда:
    - Нет доступа к БД при генерации миграции
    - Нужно получить SQL скрипт для ручного выполнения
    - Работаем в CI/CD с ограниченным доступом

    Example:
        alembic upgrade head --sql > migration.sql
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Запуск миграций в 'online' режиме

    Создаётся реальное подключение к БД и миграции применяются напрямую.
    Это режим по умолчанию для обычной работы.

    Используется когда:
    - Есть доступ к БД
    - Нужно применить миграции немедленно
    - Работаем в development/production

    Example:
        alembic upgrade head
    """

    # Настраиваем подключение к БД
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=database_url,
    )

    # Применяем миграции
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# ==========================================
# ЗАПУСК
# ==========================================

# Alembic автоматически выбирает режим на основе флагов командной строки
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
