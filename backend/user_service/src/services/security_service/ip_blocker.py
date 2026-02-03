
""" Временная блокировка IP адресов """

import ipaddress
from typing import Optional


class IpBlocker:

    def __init__(self, config):
        self.config = config

    def block_ip_address(
            self,
            ip_address: str,
            reason: str,
            duration_hours: Optional[int],
            admin_id: Optional[str]
    ) -> bool:
        """Блокировка IP адреса"""

        # Здесь должна быть логика блокировки IP в системе
        # Пока возвращаем True как заглушку
        return True

    def validate_ip_address(self, ip_address: str) -> bool:
        """Валидация IP адреса"""
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False
