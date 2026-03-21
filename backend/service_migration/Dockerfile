# === Базовый образ ===
FROM python:3.12-slim

# === Рабочая директория ===
WORKDIR /app

# === Системные зависимости ===
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# === Python зависимости ===
COPY backend/service_migration/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
# === Код сервиса ===
COPY backend/service_migration/ ./backend/service_migration/
COPY backend/shared/ ./backend/shared/


# === Запуск миграций ===
CMD ["python", "backend/service_migration/main.py"]