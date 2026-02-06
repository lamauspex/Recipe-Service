
from ..base import BaseUsecase


class PremissionUsecase(BaseUsecase):
    """Usecase для проверки прав пользователя"""

    def user_has_permission(self, user: User, permission: str) -> bool:

        for role in user.roles:
            if permission in role.permissions:
                return True
        return False
