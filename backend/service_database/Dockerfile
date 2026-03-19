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

# === Python зависимости (кэшируются отдельно от кода) ===
COPY backend/service_database/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# === Код сервиса ===
COPY backend/service_database/ ./backend/service_database/

# === Shared (логирование + модели для миграций) ===
COPY backend/shared/ ./backend/shared/

# === Установка shared как локальный пакет ===
RUN pip install -e ./backend/shared/

# === Переменные окружения ===
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# === Запуск ===
CMD ["python", "backend/service_database/main.py"]