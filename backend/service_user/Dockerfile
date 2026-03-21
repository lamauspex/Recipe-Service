FROM python:3.12-slim

# === Рабочая директория ===
WORKDIR /app

# === Python зависимости  ===
COPY backend/service_user/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# === Код сервиса ===
COPY backend/service_user/ ./backend/service_user/
# === Shared (логирование + модели + бд) ===
COPY backend/shared/ ./backend/shared/
COPY backend/service_user/.env .env


# === Переменные окружения ===
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# === Запуск ===
CMD ["python", "backend/service_user/main.py"]