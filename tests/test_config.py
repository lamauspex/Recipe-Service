"""
Конфигурационный файл для тестов
"""
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from backend.services.user_service.src.services.user_service import UserService
from backend.services.user_service.src.schemas import UserCreate
from backend.services.user_service.src.services.auth_service import AuthService
from backend.services.user_service.src.models import User, RefreshToken, Base


# Единая тестовая база данных в корне проекта
TEST_DATABASE_PATH = os.path.join(os.getcwd(), "test.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_PATH}"

# Настройки движка для тестов с поддержкой UUID
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # Отключаем логирование SQL для чистоты вывода тестов
)

# Добавляем поддержку UUID для SQLite и другие настройки


@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    # Включаем поддержку внешних ключей
    cursor.execute("PRAGMA foreign_keys=ON")
    # Ускоряем операции с базой данных для тестов
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


# Фабрика сессий для тестов
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)

# Общие функции для управления тестовой базой данных


def create_test_tables():
    """Создание тестовых таблиц"""
    # Импортируем все модели здесь для гарантии их регистрации
    from backend.services.user_service.src.models import User, RefreshToken
    Base.metadata.create_all(bind=test_engine)
    print("Таблицы созданы успешно")


def drop_test_tables():
    """Удаление тестовых таблиц"""
    Base.metadata.drop_all(bind=test_engine)


def cleanup_test_data(db_session):
    """Очистка тестовых данных между тестами"""
    try:
        # Получаем инспектор для проверки существования таблиц
        inspector = inspect(db_session.bind)

        # Очищаем в правильном порядке из-за внешних ключей
        if inspector.has_table('refresh_tokens'):
            db_session.query(RefreshToken).delete()
        if inspector.has_table('users'):
            db_session.query(User).delete()
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e


def override_get_db():
    """Override для зависимости базы данных в FastAPI"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def get_test_db():
    """Получение тестовой сессии базы данных"""
    return TestingSessionLocal()

# Утилиты для тестов


def create_test_user(
    db_session,
    username="testuser",
    email="test@example.com",
    password="testpassword123",
    is_admin=False
):
    """Создание тестового пользователя"""
    user_service = UserService(db_session)
    user_data = UserCreate(
        username=username,
        email=email,
        password=password,
        full_name="Test User",
        bio="Test bio"
    )

    user = user_service.create_user(user_data)
    if is_admin:
        user.is_admin = True
        db_session.commit()
        db_session.refresh(user)

    return user


def create_test_tokens(db_session, user):
    """Создание тестовых токенов для пользователя"""
    auth_service = AuthService(db_session)
    access_token, refresh_token = auth_service.create_tokens(user)
    return access_token, refresh_token
