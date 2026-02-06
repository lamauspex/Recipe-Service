"""
Расширенный сервис для обнаружения подозрительной активности
Мигрирован из старой архитектуры с улучшениями и async поддержкой
"""


import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID

from ...interfaces.user import UserRepositoryInterface
from ...infrastructure.common.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException
)


class SuspiciousActivityDetector:
    """Расширенный детектор подозрительной активности"""

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        config: Optional[Dict[str, Any]] = None
    ):
        self.user_repository = user_repository
        self.config = config or {}

        # Конфигурация анализа
        self.max_recent_attempts = self.config.get(
            'MAX_RECENT_ATTEMPTS', 15)  # минут
        self.suspicious_user_agents = self.config.get('SUSPICIOUS_USER_AGENTS', [
            "bot", "crawler", "spider", "curl", "wget", "scraper", "python-requests"
        ])
        self.max_location_changes = self.config.get('MAX_LOCATION_CHANGES', 3)
        self.rapid_attempt_threshold = self.config.get(
            'RAPID_ATTEMPT_THRESHOLD', 5)  # попыток
        self.rapid_attempt_window = self.config.get(
            'RAPID_ATTEMPT_WINDOW', 300)  # секунд

    async def detect_suspicious_login(
        self,
        email: str,
        ip_address: str,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Обнаружение подозрительного входа

        Args:
            email: Email пользователя
            ip_address: IP адрес клиента
            user_agent: User Agent клиента

        Returns:
            Dict с результатами анализа
        """
        try:
            if not email or not ip_address:
                raise ValidationException(
                    "Email и IP адрес являются обязательными параметрами")

            suspicious_indicators = []
            risk_score = 0

            # 1. Проверка частоты попыток входа
            recent_attempts = await self._get_recent_login_attempts(email, ip_address)
            if recent_attempts > self.max_recent_attempts:
                suspicious_indicators.append({
                    "type": "frequent_attempts",
                    "description": f"Слишком много попыток входа: {recent_attempts} за {self.max_recent_attempts} минут",
                    "severity": "high",
                    "count": recent_attempts
                })
                risk_score += 30

            # 2. Географический анализ (заглушка с расширенной логикой)
            geo_analysis = await self._analyze_geographic_pattern(email, ip_address)
            if geo_analysis["is_suspicious"]:
                suspicious_indicators.append({
                    "type": "geographic_anomaly",
                    "description": geo_analysis["description"],
                    "severity": geo_analysis["severity"],
                    "details": geo_analysis["details"]
                })
                risk_score += geo_analysis["risk_score"]

            # 3. Анализ User Agent
            ua_analysis = self._analyze_user_agent(user_agent)
            if ua_analysis["is_suspicious"]:
                suspicious_indicators.append({
                    "type": "suspicious_user_agent",
                    "description": ua_analysis["description"],
                    "severity": ua_analysis["severity"],
                    "user_agent": user_agent
                })
                risk_score += ua_analysis["risk_score"]

            # 4. Анализ времени входа
            time_analysis = self._analyze_login_time()
            if time_analysis["is_suspicious"]:
                suspicious_indicators.append({
                    "type": "unusual_time",
                    "description": time_analysis["description"],
                    "severity": time_analysis["severity"],
                    "login_hour": time_analysis["hour"]
                })
                risk_score += time_analysis["risk_score"]

            # 5. Анализ скоростных попыток
            rapid_analysis = await self._analyze_rapid_attempts(email, ip_address)
            if rapid_analysis["is_suspicious"]:
                suspicious_indicators.append({
                    "type": "rapid_attempts",
                    "description": rapid_analysis["description"],
                    "severity": "high",
                    "attempts_count": rapid_analysis["attempts_count"],
                    "time_window": rapid_analysis["time_window"]
                })
                risk_score += 25

            # 6. Анализ изменений в паттернах
            pattern_analysis = await self._analyze_login_patterns(email, ip_address)
            if pattern_analysis["is_suspicious"]:
                suspicious_indicators.append({
                    "type": "pattern_change",
                    "description": pattern_analysis["description"],
                    "severity": pattern_analysis["severity"],
                    "changes": pattern_analysis["changes"]
                })
                risk_score += pattern_analysis["risk_score"]

            # Расчет общего уровня риска
            risk_level = self._calculate_risk_level(risk_score)

            result = {
                "is_suspicious": risk_level in ["medium", "high", "critical"],
                "risk_level": risk_level,
                "risk_score": risk_score,
                "indicators": suspicious_indicators,
                "recommendations": self._get_recommendations(risk_level, suspicious_indicators),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }

            return {
                "success": True,
                "data": result
            }

        except ValidationException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "VALIDATION_ERROR"
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при анализе подозрительной активности: {str(e)}")

    async def get_login_history(
        self,
        email: str,
        days: int = 7,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Получение истории входов пользователя

        Args:
            email: Email пользователя
            days: Количество дней для анализа
            limit: Максимальное количество записей

        Returns:
            Dict с историей входов
        """
        try:
            if not email:
                raise ValidationException(
                    "Email является обязательным параметром")

            if days < 1 or days > 365:
                raise ValidationException("Days must be between 1 and 365")

            # Получаем пользователя
            user = await self.user_repository.get_by_email(email)
            if not user:
                raise NotFoundException(
                    f"Пользователь с email {email} не найден")

            # Получаем историю входов из репозитория
            login_history = await self.user_repository.get_login_history(str(user.id), days=days, limit=limit)

            # Форматируем историю
            formatted_history = []
            for record in login_history:
                formatted_history.append({
                    "login_time": record.get("timestamp", ""),
                    "ip_address": record.get("ip_address", ""),
                    "user_agent": record.get("user_agent", ""),
                    "success": record.get("success", False),
                    "location": record.get("location", "Unknown")
                })

            # Анализ паттернов в истории
            pattern_analysis = await self._analyze_login_patterns(email, ip_address=None, history=login_history)

            return {
                "success": True,
                "data": {
                    "email": email,
                    "period_days": days,
                    "login_count": len(formatted_history),
                    "history": formatted_history,
                    "pattern_analysis": pattern_analysis,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }

        except (ValidationException, NotFoundException) as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": type(e).__name__
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении истории входов: {str(e)}")

    async def _get_recent_login_attempts(
        self,
        email: str,
        ip_address: str,
        minutes: int = 15
    ) -> int:
        """Получение количества недавних попыток входа"""
        try:
            # Получаем пользователя
            user = await self.user_repository.get_by_email(email)
            if not user:
                return 0

            # Получаем недавние попытки из репозитория
            recent_attempts = await self.user_repository.get_recent_login_attempts(
                str(user.id),
                minutes=minutes,
                limit=1000
            )

            # Подсчитываем попытки с данного IP
            ip_attempts = 0
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)

            for attempt in recent_attempts:
                attempt_time = attempt.get("timestamp")
                if attempt_time:
                    try:
                        # Парсим время попытки
                        if isinstance(attempt_time, str):
                            parsed_time = datetime.fromisoformat(
                                attempt_time.replace('Z', '+00:00'))
                        else:
                            parsed_time = attempt_time

                        if parsed_time >= cutoff_time and attempt.get("ip_address") == ip_address:
                            ip_attempts += 1
                    except Exception:
                        continue

            return ip_attempts

        except Exception:
            return 0

    async def _analyze_geographic_pattern(
        self,
        email: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """Анализ географических паттернов (заглушка с расширенной логикой)"""
        try:
            # Получаем историю локаций пользователя
            user = await self.user_repository.get_by_email(email)
            if not user:
                return {"is_suspicious": False}

            # Получаем недавние логины (последние 30 дней)
            login_history = await self.user_repository.get_login_history(
                str(user.id),
                days=30,
                limit=100
            )

            # Анализируем уникальные локации
            unique_locations = set()
            recent_locations = []

            for record in login_history:
                location = record.get("location", "Unknown")
                unique_locations.add(location)
                recent_locations.append(location)

            # Проверяем резкие изменения локации
            if len(recent_locations) >= 2:
                last_location = recent_locations[0] if recent_locations else None
                previous_locations = recent_locations[1:6]  # Последние 5

                # Если новая локация сильно отличается от предыдущих
                if (last_location != "Unknown" and
                    len(set(previous_locations)) > 1 and  # Разные локации
                        last_location not in previous_locations):

                    return {
                        "is_suspicious": True,
                        "description": f"Необычная смена локации: {last_location}",
                        "severity": "medium",
                        "details": {
                            "current_location": last_location,
                            "previous_locations": previous_locations[:3],
                            "unique_locations_count": len(unique_locations)
                        },
                        "risk_score": 20
                    }

            return {"is_suspicious": False}

        except Exception:
            return {"is_suspicious": False}

    def _analyze_user_agent(self, user_agent: Optional[str]) -> Dict[str, Any]:
        """Анализ User Agent"""
        if not user_agent:
            return {"is_suspicious": False}

        user_agent_lower = user_agent.lower()

        # Проверка подозрительных паттернов
        for pattern in self.suspicious_user_agents:
            if pattern in user_agent_lower:
                return {
                    "is_suspicious": True,
                    "description": f"Подозрительный User Agent: содержит '{pattern}'",
                    "severity": "high",
                    "risk_score": 25
                }

        # Проверка слишком короткого User Agent
        if len(user_agent) < 10:
            return {
                "is_suspicious": True,
                "description": "Подозрительно короткий User Agent",
                "severity": "medium",
                "risk_score": 15
            }

        # Проверка подозрительных символов
        if re.search(r'[<>"\']', user_agent):
            return {
                "is_suspicious": True,
                "description": "User Agent содержит подозрительные символы",
                "severity": "high",
                "risk_score": 30
            }

        return {"is_suspicious": False}

    def _analyze_login_time(self) -> Dict[str, Any]:
        """Анализ времени входа"""
        current_hour = datetime.utcnow().hour
        current_weekday = datetime.utcnow().weekday()

        # Подозрительное время: 3-5 часов утра
        if 3 <= current_hour <= 5:
            return {
                "is_suspicious": True,
                "description": f"Вход в подозрительное время: {current_hour}:00",
                "severity": "medium",
                "hour": current_hour,
                "risk_score": 15
            }

        # Подозрительное время: выходные дни (для деловых аккаунтов)
        if current_weekday >= 5:  # Суббота, воскресенье
            return {
                "is_suspicious": True,
                "description": f"Вход в выходной день: {current_weekday}",
                "severity": "low",
                "hour": current_hour,
                "risk_score": 10
            }

        return {"is_suspicious": False}

    async def _analyze_rapid_attempts(
        self,
        email: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """Анализ быстрых последовательных попыток"""
        try:
            user = await self.user_repository.get_by_email(email)
            if not user:
                return {"is_suspicious": False}

            # Получаем недавние попытки
            recent_attempts = await self.user_repository.get_recent_login_attempts(
                str(user.id),
                minutes=10,
                limit=50
            )

            # Фильтруем попытки по IP
            ip_attempts = [
                attempt for attempt in recent_attempts
                if attempt.get("ip_address") == ip_address
            ]

            if len(ip_attempts) < self.rapid_attempt_threshold:
                return {"is_suspicious": False}

            # Сортируем по времени
            sorted_attempts = sorted(
                ip_attempts,
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )

            # Проверяем временные интервалы
            rapid_count = 1
            max_interval = timedelta(seconds=self.rapid_attempt_window)

            for i in range(1, len(sorted_attempts)):
                try:
                    current_time = datetime.fromisoformat(
                        sorted_attempts[i-1]["timestamp"].replace('Z', '+00:00'))
                    prev_time = datetime.fromisoformat(
                        sorted_attempts[i]["timestamp"].replace('Z', '+00:00'))

                    if current_time - prev_time <= max_interval:
                        rapid_count += 1
                    else:
                        break
                except Exception:
                    continue

            if rapid_count >= self.rapid_attempt_threshold:
                return {
                    "is_suspicious": True,
                    "description": f"Обнаружено {rapid_count} быстрых попыток входа",
                    "attempts_count": rapid_count,
                    "time_window": self.rapid_attempt_window
                }

            return {"is_suspicious": False}

        except Exception:
            return {"is_suspicious": False}

    async def _analyze_login_patterns(
        self,
        email: str,
        ip_address: Optional[str] = None,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Анализ изменений в паттернах входа"""
        try:
            user = await self.user_repository.get_by_email(email)
            if not user:
                return {"is_suspicious": False}

            # Получаем историю, если не передана
            if history is None:
                login_history = await self.user_repository.get_login_history(
                    str(user.id),
                    days=30,
                    limit=100
                )
            else:
                login_history = history

            if len(login_history) < 5:
                return {"is_suspicious": False}

            # Анализ изменений в частоте входов
            recent_logins = login_history[:len(login_history)//2]
            older_logins = login_history[len(login_history)//2:]

            recent_count = len(recent_logins)
            older_count = len(older_logins)

            # Значительное увеличение активности
            if recent_count > older_count * 3 and recent_count >= 5:
                return {
                    "is_suspicious": True,
                    "description": f"Резкое увеличение активности: {recent_count} vs {older_count}",
                    "severity": "medium",
                    "changes": {
                        "recent_count": recent_count,
                        "older_count": older_count,
                        "increase_factor": recent_count / max(older_count, 1)
                    },
                    "risk_score": 20
                }

            return {"is_suspicious": False}

        except Exception:
            return {"is_suspicious": False}

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

    def _get_recommendations(self, risk_level: str, indicators: List[Dict[str, Any]]) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []

        # Общие рекомендации по уровню риска
        risk_recommendations = {
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
                "Обратиться в службу поддержки",
                "Провести полный аудит безопасности"
            ]
        }

        recommendations.extend(risk_recommendations.get(risk_level, []))

        # Специфические рекомендации по индикаторам
        indicator_types = {ind.get("type") for ind in indicators}

        if "frequent_attempts" in indicator_types:
            recommendations.append("Увеличить интервал между попытками входа")
        if "geographic_anomaly" in indicator_types:
            recommendations.append(
                "Включить уведомления о входах из новых локаций")
        if "suspicious_user_agent" in indicator_types:
            recommendations.append(
                "Проверить браузер и устройство на вредоносное ПО")
        if "rapid_attempts" in indicator_types:
            recommendations.append(
                "Включить автоматическую блокировку при быстрых попытках")

        return list(set(recommendations))  # Удаляем дубликаты
