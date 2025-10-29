"""
Мидлвары user-service
"""
from .exception_handler import setup_exception_handlers
from .jwt_middleware import JWTBearer, AdminBearer
