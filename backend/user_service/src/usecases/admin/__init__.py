"""
Admin usecases package
"""

from .assign_role_to_user import AssignRoleToUserUsecase
from .check_user_permission import CheckUserPermissionUsecase
from .create_role import CreateRoleUsecase
from .delete_role import DeleteRoleUsecase
from .delete_user import DeleteUserUsecase
from .get_failed_login_attempts import GetFailedLoginAttemptsUsecase
from .get_login_history import GetLoginHistoryUsecase
from .get_login_statistics import GetLoginStatisticsUsecase
from .get_role import GetRoleUsecase
from .get_suspicious_activity import GetSuspiciousActivityUsecase
from .get_users import GetUsersUsecase
from .get_user_activity import GetUserActivityUsecase
from .get_user_by_id import GetUserByIdUsecase
from .get_user_roles import GetUserRolesUsecase
from .list_roles import ListRolesUsecase
from .lock_user import LockUserUsecase
from .log_login_attempt import LogLoginAttemptUsecase
from .manage_user_permissions import ManageUserPermissionsUsecase
from .remove_role_from_user import RemoveRoleFromUserUsecase
from .search_users import SearchUsersUsecase
from .unlock_user import UnlockUserUsecase
from .update_role import UpdateRoleUsecase
from .update_user import UpdateUserUsecase
from .update_user_status import UpdateUserStatusUsecase
from .user_has_permission import UserHasPermissionUsecase

__all__ = [
    "AssignRoleToUserUsecase",
    "CheckUserPermissionUsecase",
    "CreateRoleUsecase",
    "DeleteRoleUsecase",
    "DeleteUserUsecase",
    "GetFailedLoginAttemptsUsecase",
    "GetLoginHistoryUsecase",
    "GetLoginStatisticsUsecase",
    "GetRoleUsecase",
    "GetSuspiciousActivityUsecase",
    "GetUsersUsecase",
    "GetUserActivityUsecase",
    "GetUserByIdUsecase",
    "GetUserRolesUsecase",
    "ListRolesUsecase",
    "LockUserUsecase",
    "LogLoginAttemptUsecase",
    "ManageUserPermissionsUsecase",
    "RemoveRoleFromUserUsecase",
    "SearchUsersUsecase",
    "UnlockUserUsecase",
    "UpdateRoleUsecase",
    "UpdateUserUsecase",
    "UpdateUserStatusUsecase",
    "UserHasPermissionUsecase"
]
