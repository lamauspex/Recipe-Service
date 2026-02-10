
from typing import Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session

from backend.user_service.duble_service_dtoschemas.models.role_model import RoleModel


class SQLRoleRepository:
    """
    SQLAlchemy реализация репозитория ролей.

    Обёртка над существующим RoleRepository для соответствия Protocol.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_role_by_name(
        self,
        role_name: str
    ) -> Optional[RoleModel]:
        """Поиск роли по имени"""

        return self.db.query(RoleModel).filter(
            and_(
                RoleModel.name == role_name,
                RoleModel.is_active is True
            )
        ).first()
