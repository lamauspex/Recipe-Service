"""Сервис для работы с логинами и попытками входа"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from backend.user_service.src.models import User
from backend.user_service.src.repository import UserRepository


logger = logging.getLogger(__name__)


class LoginAttemptsService:
    """Сервис для работы с логинами и попытками входа"""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.user_repo = UserRepository(db_session)

    def get_login_logs(
        self,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        days: int = 7,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Получение логов входов - возвращает готовый ответ"""

        try:
            # Базовый запрос
            query = self.db.query(User)

            # Фильтрация по пользователю
            if user_id:
                query = query.filter(User.id == user_id)

            # Фильтрация по IP
            if ip_address:
                query = query.filter(User.last_login_ip == ip_address)

            # Фильтрация по времени
            if days > 0:
                since_date = datetime.now() - timedelta(days=days)
                query = query.filter(User.updated_at >= since_date)

            # Сортировка по времени входа (новые сверху)
            query = query.order_by(desc(User.updated_at))

            # Ограничение количества записей
            if limit > 0:
                query = query.limit(limit)

            users = query.all()

            # Форматируем результат
            logs = []
            for user in users:
                logs.append({
                    "user_id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "last_login_ip": user.last_login_ip,
                    "last_login_time": user.updated_at.isoformat() if user.updated_at else None,
                    "login_success": user.is_active and not user.is_locked,
                    "login_count_recent": 1  # Упрощенно, в реальности нужно считать
                })

            return logs

        except Exception as e:
            logger.error(f"Ошибка при получении логов входов: {e}")
            return []

    def get_login_logs_response(
        self,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        days: int = 7,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Получение логов входов - возвращает готовый ответ"""

        logs = self.get_login_logs(
            user_id=user_id,
            ip_address=ip_address,
            days=days,
            limit=limit
        )

        return {
            "logs": logs,
            "total_count": len(logs),
            "filters": {
                "user_id": str(user_id) if user_id else None,
                "ip_address": ip_address,
                "days": days,
                "limit": limit
            },
            "timestamp": datetime.now().isoformat()
        }
