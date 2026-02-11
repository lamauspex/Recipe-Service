
from typing import Protocol, Optional

from back.role_model import RoleModel


class RoleRepositoryProtocol(Protocol):
    """
    Protocol (интерфейс) для репозитория ролей.

    Этот Protocol может использоваться ЛЮБЫМИ сервисами,
    которым нужно работать с ролями, не только RegisterService!
    """

    def get_role_by_name(self, role_name: str) -> Optional[RoleModel]:
        """
        Поиск роли по имени

        :param role_name: Название роли
        :return: Роль или None
        """
        ...

    def get_role_by_id(self, role_id: str) -> Optional[RoleModel]:
        """
        Поиск роли по ID

        :param role_id: ID роли
        :return: Роль или None
        """
        ...

    def create_role(self, role_data: dict) -> RoleModel:
        """
        Создание новой роли

        :param role_data: Данные роли
        :return: Созданная роль
        """
        ...
