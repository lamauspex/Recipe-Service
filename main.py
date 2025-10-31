from backend.shared.config import get_settings
import subprocess
import sys
from contextlib import asynccontextmanager
from uvicorn import run as uvi_run
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from backend.services.user_service.src.api.routes import router
from backend.services.user_service.src.database.connection import init_db
from backend.shared.user_service.src_exception_handler import (
    setup_exception_handlers
)


"""
Точка входа приложения
Использует общую конфигурацию из backend.shared
Поддерживает раздельный запуск сервисов в разработке
"""


def run_service(service_name: str) -> None:
    """
    Запуск конкретного сервиса

    Args:
        service_name: имя сервиса ('user_service', 'recipe_service')
    """

    service_main_files = {
        'user_service': 'backend/services/user_service/src/main.py',
        'recipe_service': 'backend/services/recipe_service/src/main.py'
    }

    if service_name not in service_main_files:
        print(f"Ошибка: сервис '{service_name}' не найден")
        print(f"Доступные сервисы: {list(service_main_files.keys())}")
        return

    main_file = service_main_files[service_name]

    try:
        print(f"Запуск {service_name}...")

        # Запуск сервиса с помощью uvicorn
        settings = get_settings()
        port = settings.get_service_port(service_name)

        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            f'{main_file.replace("/", ".").replace(".py", "")}:app',
            '--host', '0.0.0.0',
            '--port', str(port),
            '--reload'
        ], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Ошибка при запуске {service_name}: {e}")
    except KeyboardInterrupt:
        print(f"\n{service_name} остановлен")


def test_database_connection(service_name: str) -> None:
    """
    Тестирование подключения к БД для сервиса
    """

    try:
        if service_name == 'user_service':
            from backend.services.user_service.src.database.connection import test_connection
        elif service_name == 'recipe_service':
            from backend.services.recipe_service.src.database.connection import test_connection
        else:
            print(f"Ошибка: сервис '{service_name}' не поддерживается")
            return

        if test_connection():
            print(f"Подключение БД для {service_name} успешно")
        else:
            print(f"Ошибка подключения БД для {service_name}")

    except ImportError as e:
        print(f"Ошибка импорта модуля для {service_name}: {e}")


def init_database(service_name: str) -> None:
    """
    Инициализация БД для сервиса
    """

    try:
        if service_name == 'user_service':
            from backend.services.user_service.src.database.connection import init_db
        elif service_name == 'recipe_service':
            from backend.services.recipe_service.src.database.connection import init_db
        else:
            print(f"Ошибка: сервис '{service_name}' не поддерживается")
            return

        print(f"Инициализация БД для {service_name}...")
        init_db()
        print(f"БД для {service_name} инициализирована")

    except ImportError as e:
        print(f"Ошибка импорта модуля для {service_name}: {e}")
    except Exception as e:
        print(f"Ошибка инициализации БД для {service_name}: {e}")


def show_help():
    """Показать справку по использованию"""

    print("""
Использование:
    python main.py <command> <service_name>

Команды:
    run     - запустить сервис
    test    - проверить подключение БД
    init    - инициализировать БД
    help    - показать справку

Сервисы:
    user_service   - сервис пользователей
    recipe_service - сервис рецептов

Примеры:
    python main.py run user_service
    python main.py test recipe_service
    python main.py init user_service
    """)


def main():
    """Основная функция"""

    if len(sys.argv) < 3:
        show_help()
        return

    command = sys.argv[1]
    service_name = sys.argv[2]

    commands = {
        'run': run_service,
        'test': test_database_connection,
        'init': init_database,
        'help': lambda _: show_help()
    }

    if command not in commands:
        print(f"Ошибка: неизвестная команда '{command}'")
        show_help()
        return

    # Выполнение команды
    commands[command](service_name)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        main()
    else:
        # Получаем настройки
        settings = get_settings()

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Lifespan для управления состоянием приложения"""
            # Код при запуске приложения
            init_db()
            print(
                f"{settings.SERVICE_NAME} started on port {settings.SERVICE_PORT}"
            )
            yield
            # Код при остановке приложения
            print(f"{settings.SERVICE_NAME} shutting down.")

        app = FastAPI(
            title="User Service API",
            description="Сервис управления пользователями",
            version="1.0.0",
            lifespan=lifespan
        )

        # Настройка CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Настройка обработчиков ошибок
        setup_exception_handlers(app)

        # Подключение роутеров
        app.include_router(router)

        @app.get("/")
        async def root():
            """Корневой эндпоинт с информацией о сервисе"""
            return {
                "service": settings.SERVICE_NAME,
                "version": "1.0.0",
                "environment": settings.ENVIRONMENT,
                "status": "running"
            }

        uvi_run(app, host="0.0.0.0", port=int(settings.SERVICE_PORT))
