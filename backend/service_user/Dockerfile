FROM python:3.12-slim


# === Рабочая директория ===
WORKDIR /app


# === Системные зависимости ===
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# === Python зависимости  ===
COPY backend/service_user/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt


# === Код сервиса ===
COPY backend/service_user/ ./backend/service_user/

# === Shared ===
COPY backend/shared/ ./backend/shared/
COPY backend/service_user/.env .env

# === Переменные окружения ===
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# === Запуск ===
CMD ["python", "backend/service_user/main.py"]