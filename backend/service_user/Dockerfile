FROM python:3.12-slim

# === Рабочая директория ===
WORKDIR /app_u

# === Python зависимости (кэшируются отдельно от кода) ===
COPY backend/service_user/requirements.txt ./requirements_u.txt
RUN pip install --no-cache-dir -r requirements_u.txt

# === Код сервиса ===
COPY backend/service_user/ ./backend/service_user/
# === Shared (логирование + модели для миграций) ===
COPY backend/shared/ ./backend/shared/
COPY backend/service_user/.env .env


# === Переменные окружения ===
ENV PYTHONPATH=/app_u
ENV PYTHONUNBUFFERED=2

# === Запуск ===
CMD ["python", "backend/service_user/main.py"]