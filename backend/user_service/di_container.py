"""
Контейнер зависимостей для сервисов
"""
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

# Импорты репозиториев
from backend.user_service.src.repositories.user_repository import UserRepository
from backend.user_service.src.repositories.login_attempt_repository import LoginAttemptRepository

# Импорты сервисов
from backend.user_service.src.user_service.infrastructure.services.auth_service import AuthService
from backend.user_service.src.user_service.infrastructure.services.user_management_service import UserManagementService

# Импорты usecases
from backend.user_service.src.user_service.usecases.auth.login import LoginUsecase
from backend.user_service.src.user_service.usecases.auth.register import RegisterUsecase
from backend.user_service.src.user_service.usecases.auth.refresh_token import RefreshTokenUsecase
from backend.user_service.src.user_service.usecases.auth.logout import LogoutUsecase
from backend.user_service.src.user_service.usecases.user.create_user import CreateUserUsecase
from backend.user_service.src.user_service.usecases.user.get_users import GetUsersUsecase
from backend.user_service.src.user_service.usecases.user.get_user_by_id import GetUserByIdUsecase
from backend.user_service.src.user_service.usecases.user.update_user import UpdateUserUsecase
from backend.user_service.src.user_service.usecases.user.delete_user import DeleteUserUsecase
from backend.user_service.src.user_service.usecases.user.change_password import ChangePasswordUsecase

# Импорты admin usecases
from backend.user_service.src.user_service.usecases.admin.get_users import GetUsersUsecase as AdminGetUsersUsecase
from backend.user_service.src.user_service.usecases.admin.get_user_by_id import GetUserByIdUsecase as AdminGetUserByIdUsecase
from backend.user_service.src.user_service.usecases.admin.update_user_status import UpdateUserStatusUsecase
from backend.user_service.src.user_service.usecases.admin.delete_user import DeleteUserUsecase as AdminDeleteUserUsecase
from backend.user_service.src.user_service.usecases.admin.get_user_activity import GetUserActivityUsecase
from backend.user_service.src.user_service.usecases.admin.search_users import SearchUsersUsecase

# Импорты мониторинга входов
from backend.user_service.src.user_service.usecases.monitoring.log_login_attempt import LogLoginAttemptUsecase
from backend.user_service.src.user_service.usecases.monitoring.get_login_history import GetLoginHistoryUsecase
from backend.user_service.src.user_service.usecases.monitoring.get_login_statistics import GetLoginStatisticsUsecase


class DIContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей"""

    # Конфигурация
    config = providers.Configuration()

    # Репозитории
    user_repository = providers.Factory(
        UserRepository,
        session_factory=Provide["database.session_factory"]
    )

    login_attempt_repository = providers.Factory(
        LoginAttemptRepository,
        session_factory=Provide["database.session_factory"]
    )

    # === Usecases ===

    # Auth usecases
    login_usecase = providers.Factory(
        LoginUsecase,
        user_repository=user_repository,
        password_hasher=Provide["password_hasher"],
        jwt_handler=Provide["jwt_handler"],
        login_attempt_repository=login_attempt_repository
    )

    register_usecase = providers.Factory(
        RegisterUsecase,
        user_repository=user_repository,
        password_hasher=Provide["password_hasher"]
    )

    refresh_token_usecase = providers.Factory(
        RefreshTokenUsecase,
        user_repository=user_repository,
        jwt_handler=Provide["jwt_handler"]
    )

    logout_usecase = providers.Factory(
        LogoutUsecase,
        jwt_handler=Provide["jwt_handler"]
    )

    # User usecases
    create_user_usecase = providers.Factory(
        CreateUserUsecase,
        user_repository=user_repository,
        password_hasher=Provide["password_hasher"]
    )

    get_users_usecase = providers.Factory(
        GetUsersUsecase,
        user_repository=user_repository
    )

    get_user_by_id_usecase = providers.Factory(
        GetUserByIdUsecase,
        user_repository=user_repository
    )

    update_user_usecase = providers.Factory(
        UpdateUserUsecase,
        user_repository=user_repository
    )

    delete_user_usecase = providers.Factory(
        DeleteUserUsecase,
        user_repository=user_repository
    )

    change_password_usecase = providers.Factory(
        ChangePasswordUsecase,
        user_repository=user_repository,
        password_hasher=Provide["password_hasher"]
    )

    # === Admin usecases ===

    admin_get_users_usecase = providers.Factory(
        AdminGetUsersUsecase,
        user_repository=user_repository
    )

    admin_get_user_by_id_usecase = providers.Factory(
        AdminGetUserByIdUsecase,
        user_repository=user_repository
    )

    update_user_status_usecase = providers.Factory(
        UpdateUserStatusUsecase,
        user_repository=user_repository
    )

    admin_delete_user_usecase = providers.Factory(
        AdminDeleteUserUsecase,
        user_repository=user_repository
    )

    get_user_activity_usecase = providers.Factory(
        GetUserActivityUsecase,
        user_repository=user_repository,
        activity_repository=login_attempt_repository
    )

    search_users_usecase = providers.Factory(
        SearchUsersUsecase,
        user_repository=user_repository
    )

    # === Monitoring usecases ===

    log_login_attempt_usecase = providers.Factory(
        LogLoginAttemptUsecase,
        login_attempt_repository=login_attempt_repository
    )

    get_login_history_usecase = providers.Factory(
        GetLoginHistoryUsecase,
        login_attempt_repository=login_attempt_repository
    )

    get_login_statistics_usecase = providers.Factory(
        GetLoginStatisticsUsecase,
        login_attempt_repository=login_attempt_repository
    )

    # === Сервисы ===

    # Auth сервис
    auth_service = providers.Factory(
        AuthService,
        login_usecase=login_usecase,
        register_usecase=register_usecase,
        refresh_token_usecase=refresh_token_usecase,
        logout_usecase=logout_usecase,
        create_user_usecase=create_user_usecase,
        get_users_usecase=get_users_usecase,
        get_user_by_id_usecase=get_user_by_id_usecase,
        update_user_usecase=update_user_usecase,
        delete_user_usecase=delete_user_usecase,
        change_password_usecase=change_password_usecase
    )

    # User Management сервис
    user_management_service = providers.Factory(
        UserManagementService,
        user_repository=user_repository,
        activity_repository=login_attempt_repository,
        get_users_usecase=admin_get_users_usecase,
        get_user_by_id_usecase=admin_get_user_by_id_usecase,
        update_user_status_usecase=update_user_status_usecase,
        delete_user_usecase=admin_delete_user_usecase,
        get_user_activity_usecase=get_user_activity_usecase,
        search_users_usecase=search_users_usecase
    )

    # Admin сервис
    admin_service = providers.Factory(
        AdminService,
        user_management_service=user_management_service,
        auth_service=auth_service,
        log_login_attempt_usecase=log_login_attempt_usecase,
        get_login_history_usecase=get_login_history_usecase,
        get_login_statistics_usecase=get_login_statistics_usecase
    )


# Глобальный экземпляр контейнера
container = DIContainer()


@inject
def get_auth_service(
    auth_service: AuthService = Provide[container.auth_service]
) -> AuthService:
    """Получение сервиса аутентификации"""
    return auth_service


@inject
def get_user_management_service(
    user_management_service: UserManagementService = Provide[container.user_management_service]
) -> UserManagementService:
    """Получение сервиса управления пользователями"""
    return user_management_service


@inject
def get_admin_service(
    admin_service: AdminService = Provide[container.admin_service]
) -> AdminService:
    """Получение административного сервиса"""
    return admin_service


# Экспорт контейнера и функций
__all__ = [
    "container",
    "get_auth_service",
    "get_user_management_service",
    "get_admin_service"
]
