"""
Сервис для блокировки и управления IP адресами
Мигрирован из старой архитектуры в новую Clean Architecture
"""

import ipaddress
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from uuid import uuid4

from ...infrastructure.common.exceptions import (
    ValidationException,
    DatabaseException
)


class IpBlocker:
    """Сервис для управления блокировкой IP адресов"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.default_block_duration = self.config.get('DEFAULT_IP_BLOCK_DURATION_HOURS', 24)
        self.max_block_duration = self.config.get('MAX_IP_BLOCK_DURATION_HOURS', 168)  # 7 дней
        
        # Хранилище заблокированных IP (в реальном приложении - БД)
        self._blocked_ips: Dict[str, Dict[str, Any]] = {}

    async def block_ip_address(
        self,
        ip_address: str,
        duration_hours: Optional[int] = None,
        reason: str = "Подозрительная активность",
        block_type: str = "temporary"
    ) -> Dict[str, Any]:
        """
        Блокировка IP адреса
        
        Args:
            ip_address: IP адрес для блокировки
            duration_hours: Длительность блокировки в часах
            reason: Причина блокировки
            block_type: Тип блокировки ('temporary' или 'permanent')
            
        Returns:
            Dict с результатом операции
        """
        try:
            # Валидация IP адреса
            if not self._is_valid_ip(ip_address):
                raise ValidationException(f"Некорректный IP адрес: {ip_address}")

            # Валидация длительности блокировки
            if block_type == "temporary":
                block_duration = duration_hours or self.default_block_duration
                if block_duration > self.max_block_duration:
                    block_duration = self.max_block_duration
            else:
                block_duration = None  # permanent

            # Расчет времени разблокировки
            if block_type == "temporary":
                unblock_time = datetime.utcnow() + timedelta(hours=block_duration)
            else:
                unblock_time = None

            # Создание записи о блокировке
            block_id = str(uuid4())
            block_record = {
                "id": block_id,
                "ip_address": ip_address,
                "block_type": block_type,
                "reason": reason,
                "blocked_at": datetime.utcnow(),
                "unblock_at": unblock_time,
                "is_active": True
            }

            # Сохранение в хранилище (в реальном приложении - БД)
            self._blocked_ips[ip_address] = block_record

            return {
                "success": True,
                "message": f"IP адрес {ip_address} заблокирован",
                "data": {
                    "block_id": block_id,
                    "ip_address": ip_address,
                    "block_type": block_type,
                    "duration_hours": block_duration,
                    "reason": reason,
                    "blocked_at": datetime.utcnow().isoformat(),
                    "unblock_at": unblock_time.isoformat() if unblock_time else None
                }
            }

        except ValidationException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "INVALID_IP"
            }
        except Exception as e:
            raise DatabaseException(f"Ошибка при блокировке IP адреса: {str(e)}")

    async def unblock_ip_address(self, ip_address: str) -> Dict[str, Any]:
        """
        Разблокировка IP адреса
        
        Args:
            ip_address: IP адрес для разблокировки
            
        Returns:
            Dict с результатом операции
        """
        try:
            if not self._is_valid_ip(ip_address):
                raise ValidationException(f"Некорректный IP адрес: {ip_address}")

            if ip_address not in self._blocked_ips:
                return {
                    "success": False,
                    "error": f"IP адрес {ip_address} не найден в списке заблокированных",
                    "error_code": "IP_NOT_FOUND"
                }

            # Обновление записи
            self._blocked_ips[ip_address]["is_active"] = False
            self._blocked_ips[ip_address]["unblocked_at"] = datetime.utcnow()

            return {
                "success": True,
                "message": f"IP адрес {ip_address} разблокирован",
                "data": {
                    "ip_address": ip_address,
                    "unblocked_at": datetime.utcnow().isoformat()
                }
            }

        except ValidationException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "INVALID_IP"
            }
        except Exception as e:
            raise DatabaseException(f"Ошибка при разблокировке IP адреса: {str(e)}")

    async def is_ip_blocked(self, ip_address: str) -> Dict[str, Any]:
        """
        Проверка блокировки IP адреса
        
        Args:
            ip_address: IP адрес для проверки
            
        Returns:
            Dict с информацией о блокировке
        """
        try:
            if not self._is_valid_ip(ip_address):
                return {
                    "is_blocked": False,
                    "reason": None,
                    "unblock_at": None
                }

            if ip_address not in self._blocked_ips:
                return {
                    "is_blocked": False,
                    "reason": None,
                    "unblock_at": None
                }

            block_record = self._blocked_ips[ip_address]

            # Проверяем, активна ли блокировка
            if not block_record["is_active"]:
                return {
                    "is_blocked": False,
                    "reason": None,
                    "unblock_at": None
                }

            # Для временных блокировок проверяем срок действия
            if block_record["block_type"] == "temporary":
                if datetime.utcnow() >= block_record["unblock_at"]:
                    # Время блокировки истекло, автоматически разблокируем
                    await self.unblock_ip_address(ip_address)
                    return {
                        "is_blocked": False,
                        "reason": None,
                        "unblock_at": None
                    }

            return {
                "is_blocked": True,
                "reason": block_record["reason"],
                "block_type": block_record["block_type"],
                "blocked_at": block_record["blocked_at"].isoformat(),
                "unblock_at": block_record["unblock_at"].isoformat() if block_record["unblock_at"] else None
            }

        except Exception as e:
            # Логирование ошибки, но не прерываем выполнение
            return {
                "is_blocked": False,
                "reason": f"Ошибка проверки IP: {str(e)}",
                "unblock_at": None
            }

    async def get_blocked_ips(self, limit: int = 100) -> Dict[str, Any]:
        """
        Получение списка заблокированных IP адресов
        
        Args:
            limit: Максимальное количество записей
            
        Returns:
            Dict со списком заблокированных IP
        """
        try:
            active_blocks = []
            
            for ip_address, block_record in self._blocked_ips.items():
                if block_record["is_active"]:
                    active_blocks.append({
                        "ip_address": ip_address,
                        "block_type": block_record["block_type"],
                        "reason": block_record["reason"],
                        "blocked_at": block_record["blocked_at"].isoformat(),
                        "unblock_at": block_record["unblock_at"].isoformat() if block_record["unblock_at"] else None
                    })

            # Сортировка по времени блокировки (новые первыми)
            active_blocks.sort(key=lambda x: x["blocked_at"], reverse=True)
            
            # Ограничение количества записей
            active_blocks = active_blocks[:limit]

            return {
                "success": True,
                "data": {
                    "blocked_ips": active_blocks,
                    "total": len(active_blocks)
                }
            }

        except Exception as e:
            raise DatabaseException(f"Ошибка при получении списка заблокированных IP: {str(e)}")

    async def auto_unblock_expired(self) -> Dict[str, Any]:
        """
        Автоматическая разблокировка IP с истекшим временем блокировки
        
        Returns:
            Dict с результатом операции
        """
        try:
            current_time = datetime.utcnow()
            unblocked_count = 0

            for ip_address, block_record in list(self._blocked_ips.items()):
                if (block_record["is_active"] and 
                    block_record["block_type"] == "temporary" and 
                    block_record["unblock_at"] and 
                    current_time >= block_record["unblock_at"]):
                    
                    await self.unblock_ip_address(ip_address)
                    unblocked_count += 1

            return {
                "success": True,
                "message": f"Автоматически разблокировано {unblocked_count} IP адресов",
                "data": {
                    "unblocked_count": unblocked_count,
                    "processed_at": current_time.isoformat()
                }
            }

        except Exception as e:
            raise DatabaseException(f"Ошибка при автоматической разблокировке IP: {str(e)}")

    async def block_ip_range(
        self,
        ip_range: str,
        duration_hours: Optional[int] = None,
        reason: str = "Массовая подозрительная активность"
    ) -> Dict[str, Any]:
        """
        Блокировка диапазона IP адресов
        
        Args:
            ip_range: CIDR диапазон (например, '192.168.1.0/24')
            duration_hours: Длительность блокировки в часах
            reason: Причина блокировки
            
        Returns:
            Dict с результатом операции
        """
        try:
            # Валидация CIDR диапазона
            try:
                network = ipaddress.ip_network(ip_range, strict=False)
            except ValueError:
                raise ValidationException(f"Некорректный CIDR диапазон: {ip_range}")

            # Получаем список IP в диапазоне (ограничиваем для безопасности)
            ip_list = list(network.hosts())[:1000]  # Максимум 1000 IP

            if len(ip_list) > 1000:
                return {
                    "success": False,
                    "error": f"Диапазон слишком большой ({len(ip_list)} IP). Максимум 1000 IP за раз",
                    "error_code": "RANGE_TOO_LARGE"
                }

            blocked_count = 0
            errors = []

            for ip in ip_list:
                try:
                    result = await self.block_ip_address(
                        str(ip), 
                        duration_hours, 
                        reason, 
                        "temporary"
                    )
                    if result["success"]:
                        blocked_count += 1
                except Exception as e:
                    errors.append(f"Ошибка блокировки {ip}: {str(e)}")

            return {
                "success": True,
                "message": f"Заблокировано {blocked_count} IP адресов из диапазона {ip_range}",
                "data": {
                    "ip_range": ip_range,
                    "total_ips_in_range": len(ip_list),
                    "blocked_count": blocked_count,
                    "errors": errors
                }
            }

        except ValidationException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "INVALID_RANGE"
            }
        except Exception as e:
            raise DatabaseException(f"Ошибка при блокировке диапазона IP: {str(e)}")

    def _is_valid_ip(self, ip_address: str) -> bool:
        """
        Валидация IP адреса
        
        Args:
            ip_address: IP адрес для проверки
            
        Returns:
            bool: True если IP корректный
        """
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False
