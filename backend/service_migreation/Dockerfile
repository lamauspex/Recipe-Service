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
COPY backend/service_migreation/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# === Код сервиса ===
COPY backend/service_migreation/ ./backend/service_migreation/

# === Запуск миграций ===
CMD ["python", "backend/service_migreation/main.py"]