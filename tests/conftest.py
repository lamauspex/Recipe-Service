"""
Конфигурация фикстур для всех тестов
"""
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event, inspect
from fastapi.testclient import TestClient
from fastapi import FastAPI
import pytest
import os

from backend.services.user_service.src.database.connection import get_db
from backend.services.user_service.src.api.routes import router
from backend.services.user_service.src.services.auth_service import AuthService
from backend.services.user_service.src.schemas import UserCreate
from backend.services.user_service.src.services.user_service import UserService
from backend.services.user_service.src.models import User, RefreshToken
from backend.database.models import BaseModel


# Настройки тестовой базы данных
TEST_DATABASE_PATH = os.path.join(os.getcwd(), "test.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_PATH}"

# Движок базы данных для тестов
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)


# Настройка поддержки UUID и внешних ключей для SQLite
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


# Фабрика сессий для тестов
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="session")
def setup_test_database():
    """Настройка тестовой базы данных для всей сессии тестов"""
    # Создаем таблицы перед всеми тестами
    BaseModel.metadata.create_all(bind=test_engine)
    yield
    # Удаляем таблицы после всех тестов
    BaseModel.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(setup_test_database):
    """Фикстура для тестовой сессии базы данных"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # Очищаем данные между тестами
        cleanup_test_data(session)


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для тестового клиента"""
    # Создаем минимальное приложение для тестов
    app = FastAPI(title="Test App")
    app.include_router(router)

    # Переопределяем зависимость базы данных
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Сессия закрывается в фикстуре db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def test_user(db_session):
    """Фикстура для создания тестового пользователя"""
    return create_test_user(
        db_session,
        username="testuser",
        email="test@example.com",
        password="Testpassword123"
    )


@pytest.fixture(scope="function")
def test_admin_user(db_session):
    """Фикстура для создания тестового администратора"""
    return create_test_user(
        db_session,
        username="adminuser",
        email="admin@example.com",
        password="Adminpassword123",
        is_admin=True
    )


@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    """Фикстура для аутентифицированного клиента"""
    auth_service = AuthService(client.app.dependency_overrides[get_db]())
    access_token, _ = auth_service.create_tokens(test_user)
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client

    # Удаляем заголовок после использования
    if "Authorization" in client.headers:
        del client.headers["Authorization"]


@pytest.fixture(scope="function")
def admin_client(client, test_admin_user):
    """Фикстура для клиента с правами администратора"""
    auth_service = AuthService(client.app.dependency_overrides[get_db]())
    access_token, _ = auth_service.create_tokens(test_admin_user)
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client

    # Удаляем заголовок после использования
    if "Authorization" in client.headers:
        del client.headers["Authorization"]


# Утилитные функции для тестов
def cleanup_test_data(db_session):
    """Очистка тестовых данных между тестами"""
    try:
        db_session.rollback()
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


def create_test_user(
    db_session,
    username="testuser",
    email="test@example.com",
    password="Testpassword123",
    is_admin=False
):
    """Создание тестового пользователя"""
    user_service = UserService(db_session)
    user_data = UserCreate(
        username=username,
        email=email,
        password=password,
        full_name="Test User"
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
