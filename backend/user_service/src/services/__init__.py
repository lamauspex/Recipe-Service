"""
Сервисный слой нового поколения
Новый сервисный слой, построенный по принципам Clean Architecture:

- dto/ - Data Transfer Objects (запросы и ответы)
- infrastructure/ - Реализации (репозитории)
- usecases/ - Бизнес-логика (сценарии использования)
"""

# DTO Requests
from .dto.requests import BaseRequestDTO
from .dto.requests import LoginRequestDTO
from .dto.requests import RegisterRequestDTO
from .dto.requests import UserListRequestDTO
from .dto.requests import UserDeleteRequestDTO
from .dto.requests import UserActivityRequestDTO
from .dto.requests import UserSearchRequestDTO
from .dto.requests import UserRoleRequestDTO
from .dto.requests import RoleCreateRequestDTO
from .dto.requests import RoleUpdateRequestDTO
from .dto.requests import RoleDeleteRequestDTO
from .dto.requests import RoleAssignRequestDTO
from .dto.requests import PermissionCheckRequestDTO
from .dto.requests import UserPermissionsRequestDTO
from .dto.requests import UserLockRequestDTO
from .dto.requests import UserUnlockRequestDTO

# DTO Responses
from .dto.responses import BaseResponseDTO
from .dto.responses import UserListResponseDTO
from .dto.responses import UserDeleteResponseDTO
from .dto.responses import UserDetailResponseDTO
from .dto.responses import UserActivityResponseDTO
from .dto.responses import UserSearchResponseDTO
from .dto.responses import UserRoleResponseDTO
from .dto.responses import RoleCreateResponseDTO
from .dto.responses import RoleUpdateResponseDTO
from .dto.responses import RoleDeleteResponseDTO
from .dto.responses import RoleListResponseDTO
from .dto.responses import RoleAssignResponseDTO
from .dto.responses import PermissionCheckResponseDTO
from .dto.responses import UserPermissionsResponseDTO
from .dto.responses import UserLockResponseDTO
from .dto.responses import UserUnlockResponseDTO

# Usecases
from .usecases.base import BaseUsecase, UsecaseResult, ResponseBuilder

__all__ = [
    # DTO Requests
    "BaseRequestDTO",
    "LoginRequestDTO",
    "RegisterRequestDTO",
    "UserListRequestDTO",
    "UserDeleteRequestDTO",
    "UserActivityRequestDTO",
    "UserSearchRequestDTO",
    "UserRoleRequestDTO",
    "RoleCreateRequestDTO",
    "RoleUpdateRequestDTO",
    "RoleDeleteRequestDTO",
    "RoleAssignRequestDTO",
    "PermissionCheckRequestDTO",
    "UserPermissionsRequestDTO",
    "UserLockRequestDTO",
    "UserUnlockRequestDTO",

    # DTO Responses
    "BaseResponseDTO",
    "UserListResponseDTO",
    "UserDeleteResponseDTO",
    "UserDetailResponseDTO",
    "UserActivityResponseDTO",
    "UserSearchResponseDTO",
    "UserRoleResponseDTO",
    "RoleCreateResponseDTO",
    "RoleUpdateResponseDTO",
    "RoleDeleteResponseDTO",
    "RoleListResponseDTO",
    "RoleAssignResponseDTO",
    "PermissionCheckResponseDTO",
    "UserPermissionsResponseDTO",
    "UserLockResponseDTO",
    "UserUnlockResponseDTO",

    # Usecases
    "BaseUsecase",
    "UsecaseResult",
    "ResponseBuilder"
]
