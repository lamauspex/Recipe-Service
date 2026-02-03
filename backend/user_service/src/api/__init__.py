"""
API router module
"""
from fastapi import APIRouter

# Импортируем все роутеры
from .api_admin.user_management_routers import router as user_management_router
from .api_admin.statistics_analytics_routers import router as stats_router
from .api_admin.safety_routers import router as safety_router
from .api_user.management_routers import router as user_router
from .api_auth.auth_routers import router as auth_router
from .api_auth.register_user import router as register_router
from .health_router import router_1 as health_router
from .api_role.permissions_routers import router as role_router_p
from .api_role.roles_routers import router as role_router_b

# Создаем главный API router
api_router = APIRouter(prefix="/api/v1")

# Подключаем все роутеры с префиксами
api_router.include_router(user_management_router, prefix="/admin/users")
api_router.include_router(stats_router, prefix="/admin/stats")
api_router.include_router(safety_router, prefix="/admin/safety")
api_router.include_router(user_router, prefix="/users")
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(register_router, prefix="/auth")
api_router.include_router(health_router, prefix="")
api_router.include_router(role_router_p, prefix="/roles")
api_router.include_router(role_router_b, prefix="/roles")
