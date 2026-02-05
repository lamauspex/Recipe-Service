import logging
from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError

from backend.user_service.src.models import User

logger = logging.getLogger(__name__)


class SuspiciousDetector:
    """Класс для обнаружения подозрительной активности"""

    def __init__(self, config, db_session: Session):
        self.config = config
        self.db_session = db_session
        self.suspicious_threshold = getattr(
            config, 'SUSPICIOUS_LOGIN_THRESHOLD', 3)

    def detect_suspicious_activity(
        self,
        email: str,
        user_agent: str
    ) -> bool:
        """Обнаружение подозрительной активности"""

        try:
            # Проверяем множественные логины с разных IP
            recent_logins = self.db_session.query(User).filter(
                and_(
                    User.email == email,
                    User.updated_at >= datetime.now() - timedelta(hours=1)
                )
            ).all()

            if len(recent_logins) > 1:
                unique_ips = set(
                    login.last_login_ip for login in recent_logins if login.last_login_ip)
                if len(unique_ips) > 1:
                    logger.warning(
                        f"Подозрительная активность: {email} с {len(unique_ips)} IP адресов за час")
                    return True

            # Проверяем необычное время входа
            current_hour = datetime.now().hour
            if current_hour < 6 or current_hour > 23:  # Входы в нерабочее время
                user = self.db_session.query(User).filter(
                    User.email == email
                ).first()

                if user and user.full_name:  # Если есть данные пользователя
                    # Проверяем, часто ли пользователь входит в это время
                    night_logins = self.db_session.query(User).filter(
                        and_(
                            User.email == email,
                            User.updated_at >= datetime.now() - timedelta(days=7)
                        )
                    ).count()

                    if night_logins < 3:  # Редкие ночные входы
                        logger.warning(
                            f"Подозрительная активность: {email} в необычное время")
                        return True

            # Проверяем смену User-Agent
            if user_agent:
                recent_user_agent = self.db_session.query(User.last_login_ip).filter(
                    and_(
                        User.email == email,
                        User.updated_at >= datetime.now() - timedelta(days=7)
                    )
                ).distinct().count()

                if recent_user_agent > 3:  # Много разных IP за неделю
                    logger.warning(
                        f"Подозрительная активность: {email} с {recent_user_agent} разных локаций")
                    return True

            return False

        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при проверке подозрительной активности {email}: {e}")
            return False

    def get_suspicious_activity_response(self, email: str, user_agent: str) -> dict:
        """Проверка подозрительной активности - возвращает готовый ответ"""

        try:
            is_suspicious = self.detect_suspicious_activity(email, user_agent)

            if is_suspicious:
                return {
                    "email": email,
                    "is_suspicious": True,
                    "message": "Обнаружена подозрительная активность",
                    "recommendation": "Рекомендуется дополнительная проверка"
                }
            else:
                return {
                    "email": email,
                    "is_suspicious": False,
                    "message": "Подозрительная активность не обнаружена",
                    "recommendation": "Активность выглядит нормальной"
                }

        except Exception as e:
            logger.error(
                f"Ошибка при проверке подозрительной активности {email}: {e}")
            return {
                "email": email,
                "is_suspicious": False,
                "message": f"Ошибка проверки: {str(e)}",
                "recommendation": "Проверка не удалась, требуется ручная проверка"
            }
