"""
Usecase для обнаружения подозрительной активности
"""

from uuid import UUID
from datetime import datetime, timedelta
from typing import Dict, Any, List

from ...schemas.requests import UserActivityRequestDTO
from ...schemas.responses import UserActivityResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException


class SuspiciousActivityUsecase(BaseUsecase):
    """Usecase для обнаружения подозрительной активности"""

    def __init__(self, user_repository, security_service, **kwargs):
        self.user_repository = user_repository
        self.security_service = security_service
        super().__init__(**kwargs)

    async def execute(self, request: UserActivityRequestDTO) -> UserActivityResponseDTO:
        """Выполнение анализа подозрительной активности"""
        try:
            # Валидация UUID
            try:
                UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Валидация дней
            if request.days < 1 or request.days > 90:
                raise ValidationException("Days must be between 1 and 90")

            # Получение пользователя
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise NotFoundException("User not found")

            # Анализ подозрительной активности
            activity_analysis = await self._analyze_user_activity(request.user_id, request.days)

            # Возврат результата
            return UserActivityResponseDTO.create_success({
                "user_id": str(request.user_id),
                "analysis_period_days": request.days,
                "activity_analysis": activity_analysis,
                "recommendations": activity_analysis.get("recommendations", []),
                "generated_at": datetime.utcnow().isoformat()
            })

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(
                f"Failed to analyze suspicious activity: {str(e)}")

    async def _analyze_user_activity(self, user_id: str, days: int) -> Dict[str, Any]:
        """Анализ активности пользователя для поиска подозрительных паттернов"""
        try:
            # Получение истории входов
            login_history = await self.user_repository.get_login_history(user_id, limit=100)

            # Получение неудачных попыток входа
            failed_attempts = await self.user_repository.get_failed_login_attempts(user_id, limit=50)

            # Получение общей активности
            user_activity = await self.user_repository.get_user_activity(user_id, days=days)

            # Анализ паттернов
            suspicious_indicators = []
            risk_score = 0

            # 1. Анализ частых неудачных попыток
            failed_count = len(failed_attempts)
            if failed_count > 10:
                suspicious_indicators.append({
                    "type": "high_failed_logins",
                    "description": f"User has {failed_count} failed login attempts",
                    "severity": "high",
                    "count": failed_count
                })
                risk_score += 30

            # 2. Анализ входов из разных географических локаций (заглушка)
            unique_ips = set()
            for attempt in failed_attempts + login_history:
                if attempt.get('ip_address'):
                    unique_ips.add(attempt['ip_address'])

            if len(unique_ips) > 5:
                suspicious_indicators.append({
                    "type": "multiple_locations",
                    "description": f"Login attempts from {len(unique_ips)} different IP addresses",
                    "severity": "medium",
                    "count": len(unique_ips)
                })
                risk_score += 20

            # 3. Анализ времени входов (ночные входы, выходные)
            night_logins = 0
            weekend_logins = 0
            for attempt in login_history:
                if not attempt.get('timestamp'):
                    continue

                try:
                    timestamp = datetime.fromisoformat(
                        attempt['timestamp'].replace('Z', '+00:00'))

                    # Проверка ночного времени (23:00 - 06:00)
                    if 23 <= timestamp.hour or timestamp.hour <= 6:
                        night_logins += 1

                    # Проверка выходных дней (суббота, воскресенье)
                    if timestamp.weekday() >= 5:  # 5 = суббота, 6 = воскресенье
                        weekend_logins += 1

                except Exception:
                    continue

            if night_logins > 3:
                suspicious_indicators.append({
                    "type": "nighttime_activity",
                    "description": f"{night_logins} login attempts during nighttime hours",
                    "severity": "medium",
                    "count": night_logins
                })
                risk_score += 15

            # 4. Анализ быстрых последовательных попыток
            rapid_attempts = await self._detect_rapid_attempts(failed_attempts)
            if rapid_attempts:
                suspicious_indicators.append({
                    "type": "rapid_attempts",
                    "description": f"Detected {len(rapid_attempts)} rapid login attempts",
                    "severity": "high",
                    "details": rapid_attempts
                })
                risk_score += 25

            # 5. Анализ изменений в паттернах активности
            activity_changes = await self._detect_activity_changes(login_history, days)
            if activity_changes:
                suspicious_indicators.extend(activity_changes)
                risk_score += 10

            # Определение общего уровня риска
            if risk_score >= 70:
                risk_level = "critical"
            elif risk_score >= 40:
                risk_level = "high"
            elif risk_score >= 20:
                risk_level = "medium"
            else:
                risk_level = "low"

            # Генерация рекомендаций
            recommendations = self._generate_recommendations(
                suspicious_indicators, risk_level)

            return {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "suspicious_indicators": suspicious_indicators,
                "summary": {
                    "total_failed_attempts": failed_count,
                    "unique_ip_addresses": len(unique_ips),
                    "nighttime_logins": night_logins,
                    "weekend_logins": weekend_logins
                },
                "recommendations": recommendations,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "error": f"Failed to analyze activity: {str(e)}",
                "risk_level": "unknown",
                "risk_score": 0,
                "suspicious_indicators": [],
                "recommendations": ["Unable to complete analysis"]
            }

    async def _detect_rapid_attempts(self, attempts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Обнаружение быстрых последовательных попыток входа"""
        rapid_patterns = []

        # Сортировка попыток по времени
        sorted_attempts = sorted(
            [a for a in attempts if a.get('timestamp')],
            key=lambda x: x['timestamp']
        )

        # Поиск паттернов быстрых попыток
        for i in range(len(sorted_attempts) - 4):
            current_attempt = sorted_attempts[i]

            # Проверяем следующие 5 попыток в течение 5 минут
            rapid_count = 0
            start_time = None

            try:
                start_time = datetime.fromisoformat(
                    current_attempt['timestamp'].replace('Z', '+00:00'))

                for j in range(i, min(i + 5, len(sorted_attempts))):
                    attempt_time = datetime.fromisoformat(
                        sorted_attempts[j]['timestamp'].replace('Z', '+00:00'))

                    if (attempt_time - start_time).total_seconds() <= 300:  # 5 минут
                        rapid_count += 1
                    else:
                        break

            except Exception:
                continue

            if rapid_count >= 5:
                rapid_patterns.append({
                    "start_time": start_time.isoformat(),
                    "attempt_count": rapid_count,
                    "time_window_seconds": 300
                })

        return rapid_patterns

    async def _detect_activity_changes(self, login_history: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
        """Обнаружение изменений в паттернах активности"""
        changes = []

        # Анализ изменений в частоте входов
        if len(login_history) >= 10:
            # Разделение истории на две части
            midpoint = len(login_history) // 2
            recent_logins = login_history[:midpoint]
            older_logins = login_history[midpoint:]

            # Подсчет входов в каждой части
            recent_count = len(recent_logins)
            older_count = len(older_logins)

            # Если в последнее время активность значительно увеличилась
            if recent_count > older_count * 2 and recent_count >= 3:
                changes.append({
                    "type": "activity_spike",
                    "description": f"Recent activity increased from {older_count} to {recent_count} logins",
                    "severity": "medium",
                    "details": {
                        "recent_count": recent_count,
                        "older_count": older_count,
                        "increase_factor": recent_count / max(older_count, 1)
                    }
                })

        return changes

    def _generate_recommendations(self, indicators: List[Dict[str, Any]], risk_level: str) -> List[str]:
        """Генерация рекомендаций на основе обнаруженных индикаторов"""
        recommendations = []

        # Общие рекомендации на основе уровня риска
        if risk_level == "critical":
            recommendations.extend([
                "Immediately lock the account",
                "Require password reset",
                "Notify security team",
                "Review recent login attempts manually"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "Consider temporary account restriction",
                "Send security alert to user",
                "Increase monitoring frequency"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Monitor account activity more closely",
                "Consider implementing additional authentication"
            ])

        # Специфические рекомендации по типам индикаторов
        for indicator in indicators:
            indicator_type = indicator.get("type")

            if indicator_type == "high_failed_logins":
                recommendations.append(
                    "Implement CAPTCHA after failed attempts")
            elif indicator_type == "multiple_locations":
                recommendations.append(
                    "Require additional verification for new locations")
            elif indicator_type == "nighttime_activity":
                recommendations.append(
                    "Consider time-based access restrictions")
            elif indicator_type == "rapid_attempts":
                recommendations.append("Implement automatic account lockout")

        # Удаление дубликатов
        return list(set(recommendations))
