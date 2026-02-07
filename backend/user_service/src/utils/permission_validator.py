"""
Валидация разрешений для ролей
Проверка корректности наборов разрешений (битовая маска)
"""

from typing import List
from dataclasses import dataclass

from backend.user_service.src.schemas_dto.user_roles import Permission


@dataclass
class ValidationResult:
    """Результат валидации разрешений"""

    is_valid: bool
    invalid_permissions: List[str]
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class PermissionValidator:
    """ Класс для валидации разрешений """

    # Все доступные разрешения в системе
    AVAILABLE_PERMISSIONS = {perm.name for perm in Permission}

    @classmethod
    def validate_permissions(cls, permissions: List[str]) -> ValidationResult:
        """
        Валидация списка разрешений
        """
        if not permissions:
            return ValidationResult(
                is_valid=True,
                invalid_permissions=[],
                warnings=["Пустой список разрешений"]
            )

        # Нормализация
        unique_permissions = list(
            set(perm.strip().upper()
                for perm in permissions if perm.strip()
                ))

        # Проверка на недопустимые разрешения
        invalid_permissions = [
            perm for perm in unique_permissions
            if perm not in cls.AVAILABLE_PERMISSIONS
        ]

        is_valid = len(invalid_permissions) == 0

        return ValidationResult(
            is_valid=is_valid,
            invalid_permissions=invalid_permissions,
            warnings=[]
        )

    @classmethod
    def get_available_permissions(cls) -> List[str]:
        """Получение списка всех доступных разрешений"""

        return sorted(list(cls.AVAILABLE_PERMISSIONS))

    @classmethod
    def get_permission_description(cls, permission: str) -> str:
        """Получение описания разрешения"""

        descriptions = {
            "READ": "Чтение данных",
            "WRITE": "Создание/редактирование",
            "DELETE": "Удаление",
            "MANAGE_USERS": "Управление пользователями",
            "MANAGE_ROLES": "Управление ролями",
            "VIEW_STATS": "Просмотр статистики",
            "SYSTEM_CONFIG": "Системные настройки",
            "BAN_USERS": "Блокировка пользователей",
        }
        return descriptions.get(
            permission.upper(),
            "Неизвестное разрешение"
        )

    @classmethod
    def suggest_permissions_for_role(cls, role_type: str) -> List[str]:
        """Предложение набора разрешений для типа роли"""

        suggestions = {
            "admin": [
                "READ",
                "WRITE",
                "DELETE",
                "MANAGE_USERS",
                "MANAGE_ROLES",
                "VIEW_STATS",
                "SYSTEM_CONFIG",
                "BAN_USERS"
            ],
            "moderator": [
                "READ",
                "WRITE",
                "VIEW_STATS",
                "MANAGE_USERS"
            ],
            "user": ["READ"],
            "support": [
                "READ",
                "MANAGE_USERS"
            ],
            "analyst": [
                "READ",
                "VIEW_STATS"
            ],
        }
        return suggestions.get(role_type.lower(), [])

    @classmethod
    def check_permission_conflicts(cls, permissions: List[str]) -> List[str]:
        """Проверка конфликтов между разрешениями"""

        conflicts = []
        perm_set = set(perm.upper() for perm in permissions)

        # FULL_ACCESS включает всё
        if "FULL_ACCESS" in perm_set and len(perm_set) > 1:
            conflicts.append("FULL_ACCESS уже включает все разрешения")

        return conflicts


def validate_permissions(permissions: List[str]) -> ValidationResult:
    """Функция-обертка для валидации разрешений"""

    return PermissionValidator.validate_permissions(permissions)
