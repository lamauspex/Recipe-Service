"""
main.py — ПРОСТОЙ ЗАПУСК МИГРАЦИЙ
"""

import os
import sys

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER", "postgresql")

DATABASE_URL = (
    f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

# Проверка подключения
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
print("✓ Database connected")

# Миграции
alembic_cfg = Config("backend/service_migration/alembic.ini")
command.upgrade(alembic_cfg, "head")
print("✓ Migrations completed")
