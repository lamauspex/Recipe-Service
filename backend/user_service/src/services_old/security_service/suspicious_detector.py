import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from sqlalchemy.exc import SQLAlchemyError

from backend.user_service.src.models import User
from common.base_service import BaseService


logger = logging.getLogger(__name__)


class SuspiciousActivityDetector(BaseService):
    """Класс для обнаружения подозрительной активности"""

    def __init__(self, config, db_session: Session):
        super().__init__()
        self.config = config
        self.db_session = db_session

    def detect_suspicious_login(
        self,
        email: str,
        ip_address: str,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """Обнаружение подозрительного входа"""

        try:
            suspicious_indicators = []
            risk_score = 0

            # Проверка частоты попыток входа
            recent_attempts = self._get_recent_login_attempts(
                email, ip_address, minutes=15)
            if recent_attempts > 5:
                suspicious_indicators.append("Частые попытки входа")
                risk_score += 30

            # Проверка географической аномалии (заглушка)
            if self._is_unusual_location(ip_address):
                suspicious_indicators.append("Необычное местоположение")
                risk_score += 40

            # Проверка User Agent
            if self._is_suspicious_user_agent(user_agent):
                suspicious_indicators.append("Подозрительный User Agent")
                risk_score += 20

            # Проверка времени входа
            if self._is_unusual_time():
                suspicious_indicators.append("Необычное время входа")
                risk_score += 10

            # Определяем уровень риска
            risk_level = self._calculate_risk_level(risk_score)

            result = {
                "is_suspicious": risk_level in ["medium", "high", "critical"],
                "risk_level": risk_level,
                "risk_score": risk_score,
                "indicators": suspicious_indicators,
                "recommendations": self._get_recommendations(risk_level)
            }

            if result["is_suspicious"]:
                return self._handle_success(
                    "Обнаружена подозрительная активность",
                    data=result
                )
            else:
                return self._handle_success(
                    "Подозрительная активность не обнаружена",
                    data=result
                )

        except Exception as e:
            return self._handle_error(e, "обнаружения подозрительной активности")

    def get_login_history(self, email: str, days: int = 7) -> Dict[str, Any]:
        """Получение истории входов"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            users = self.db_session.query(User).filter(
                and_(
                    User.email == email,
                    User.last_login_at >= cutoff_date
                )
            ).order_by(desc(User.last_login_at)).all()

            history = []
            for user in users:
                history.append({
                    "login_time": user.last_login_at.isoformat(),
                    "ip_address": user.last_login_ip,
                    "user_agent": getattr(user, 'last_user_agent', None)
                })

            return self._handle_success(
                "История входов получена",
                data={
                    "email": email,
                    "period_days": days,
                    "login_count": len(history),
                    "history": history
                }
            )

        except SQLAlchemyError as e:
            return self._handle_error(e, "получения истории входов")

    def _get_recent_login_attempts(self, email: str, ip_address: str, minutes: int) -> int:
        """Получение количества недавних попыток входа"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)

        # Проверяем по email и IP
        attempts = self.db_session.query(User).filter(
            and_(
                User.email == email,
                User.updated_at >= cutoff_time
            )
        ).count()

        return attempts

    def _is_unusual_location(self, ip_address: str) -> bool:
        """Проверка необычного местоположения (заглушка)"""
        # В реальном приложении здесь был бы GeoIP lookup
        # Пока что возвращаем False
        return False

    def _is_suspicious_user_agent(self, user_agent: str = None) -> bool:
        """Проверка подозрительного User Agent"""
        if not user_agent:
            return False

        suspicious_patterns = [
            "bot", "crawler", "spider", "curl", "wget"
        ]

        user_agent_lower = user_agent.lower()
        return any(pattern in user_agent_lower for pattern in suspicious_patterns)

    def _is_unusual_time(self) -> bool:
        """Проверка необычного времени входа"""
        current_hour = datetime.now().hour

        # Подозрительно, если вход в 3-5 часов утра
        return 3 <= current_hour <= 5

    def _calculate_risk_level(self, risk_score: int) -> str:
        """Расчет уровня риска"""
        if risk_score >= 80:
            return "critical"
        elif risk_score >= 60:
            return "high"
        elif risk_score >= 30:
            return "medium"
        else:
            return "low"

    def _get_recommendations(self, risk_level: str) -> list:
        """Получение рекомендаций по безопасности"""
        recommendations = {
            "low": ["Рекомендуется включить двухфакторную аутентификацию"],
            "medium": [
                "Включить двухфакторную аутентификацию",
                "Проверить недавние входы в аккаунт"
            ],
            "high": [
                "Немедленно сменить пароль",
                "Включить двухфакторную аутентификацию",
                "Проверить все устройства и сессии"
            ],
            "critical": [
                "Заблокировать аккаунт до проверки",
                "Сменить пароль с другого устройства",
                "Обратиться в службу поддержки"
            ]
        }

        return recommendations.get(risk_level, [])
