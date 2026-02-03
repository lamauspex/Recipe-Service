

from backend.user_service.src.models import RoleModel


def get_role_description(role: RoleModel) -> str:
    """Получение описания роли"""

    descriptions = {
        RoleModel.USER: "Обычный пользователь системы",
        RoleModel.ADMIN: "Администратор с полными правами",
        RoleModel.MODERATOR: "Модератор с ограниченными правами"
    }
    return descriptions.get(role, "Неизвестная роль")
