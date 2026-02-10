from sqlalchemy.orm import Session

from backend.user_service.src.factories import RepositoryFactory
from backend.user_service.src.service.register_service.register_service import (
    RegisterService)


class RegisterServiceFactory:
    """
    Фабрика для создания RegisterService
    """

    @staticmethod
    def create(db_session: Session) -> RegisterService:
        """
        Создаёт RegisterService с нужными зависимостями

        :param db_session: Сессия базы данных из DI-контейнера
        :return: Готовый к использованию RegisterService
        """
        # 1. Создаём репозитории через фабрику
        user_repo = RepositoryFactory.create_user_repository(db_session)

        # 2. Создаём сервис с репозиторием
        service = RegisterService(user_repo=user_repo)

        return service
