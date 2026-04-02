from .container import container
from .dependencies import (
    get_db,
    get_current_user,
    get_message_publisher,
    get_recipe_service,
    get_user_service_client
)


# __getattr__ для ленивого импорта UserServiceClient
def __getattr__(name: str):
    if name == "UserServiceClient":
        from .user_grpc_client import UserServiceClient
        return UserServiceClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "container",
    "get_db",
    "get_current_user",
    "get_message_publisher",
    "get_recipe_service",
    "get_user_service_client",
    "UserServiceClient"
]
