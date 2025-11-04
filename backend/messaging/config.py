"""
Конфигурация RabbitMQ для микросервисной архитектуры
"""

from enum import Enum
from typing import Dict, List


class ExchangeType(str, Enum):
    DIRECT = 'direct'
    TOPIC = 'topic'
    FANOUT = 'fanout'
    HEADERS = 'headers'


class RabbitMQConfig:
    """Конфигурация RabbitMQ"""

    # Exchanges
    USER_EVENTS = 'user_events'
    RECIPE_EVENTS = 'recipe_events'
    NOTIFICATION_EVENTS = 'notification_events'

    # Exchange types
    EXCHANGE_TYPES: Dict[str, ExchangeType] = {
        USER_EVENTS: ExchangeType.TOPIC,
        RECIPE_EVENTS: ExchangeType.TOPIC,
        NOTIFICATION_EVENTS: ExchangeType.FANOUT,
    }

    # Routing keys для user events
    USER_ROUTING_KEYS = {
        'user_created': 'user.created',
        'user_updated': 'user.updated.*',
        'user_deleted': 'user.deleted',
        'user_premium_activated': 'user.premium.activated',
        'user_login': 'user.login',
        'user_logout': 'user.logout',
    }

    # Routing keys для recipe events
    RECIPE_ROUTING_KEYS = {
        'recipe_created': 'recipe.created',
        'recipe_updated': 'recipe.updated',
        'recipe_deleted': 'recipe.deleted',
        'recipe_rated': 'recipe.rated',
        'recipe_commented': 'recipe.commented',
    }

    # Очереди для User Service
    USER_SERVICE_QUEUES = [
        {
            'name': 'user_service.notifications',
            'exchange': NOTIFICATION_EVENTS,
            'routing_key': '*',  # Fanout exchange
        }
    ]

    # Очереди для Recipe Service
    RECIPE_SERVICE_QUEUES = [
        {
            'name': 'recipe_service.user_updates',
            'exchange': USER_EVENTS,
            'routing_key': 'user.updated.*',
        },
        {
            'name': 'recipe_service.user_deletions',
            'exchange': USER_EVENTS,
            'routing_key': 'user.deleted',
        }
    ]

    # Очереди для Preferences Service (когда будет создан)
    PREFERENCES_SERVICE_QUEUES = [
        {
            'name': 'preferences_service.user_events',
            'exchange': USER_EVENTS,
            'routing_key': 'user.*',
        },
        {
            'name': 'preferences_service.recipe_events',
            'exchange': RECIPE_EVENTS,
            'routing_key': 'recipe.*',
        }
    ]

    # Очереди для Comment Service (когда будет создан)
    COMMENT_SERVICE_QUEUES = [
        {
            'name': 'comment_service.recipe_events',
            'exchange': RECIPE_EVENTS,
            'routing_key': 'recipe.*',
        }
    ]

    @classmethod
    def get_service_queues(cls, service_name: str) -> List[Dict]:
        """Получить очереди для конкретного сервиса"""
        queues_map = {
            'user-service': cls.USER_SERVICE_QUEUES,
            'recipe-service': cls.RECIPE_SERVICE_QUEUES,
            'preferences-service': cls.PREFERENCES_SERVICE_QUEUES,
            'comment-service': cls.COMMENT_SERVICE_QUEUES,
        }
        return queues_map.get(service_name, [])

    @classmethod
    def get_routing_key(cls, event_type: str, service: str) -> str:
        """Получить routing key для события"""
        if service == 'user':
            return cls.USER_ROUTING_KEYS.get(
                event_type,
                f'user.{event_type}'
            )
        elif service == 'recipe':
            return cls.RECIPE_ROUTING_KEYS.get(
                event_type,
                f'recipe.{event_type}'
            )
        else:
            return f'{service}.{event_type}'


# Схемы событий
class EventSchemas:
    """Схемы событий для валидации"""

    USER_CREATED = {
        'type': 'object',
        'properties': {
            'user_id': {'type': 'string'},
            'username': {'type': 'string'},
            'email': {'type': 'string'},
            'timestamp': {'type': 'string'},
            'event_type': {'type': 'string'}
        },
        'required': ['user_id', 'username', 'email', 'timestamp', 'event_type']
    }

    USER_UPDATED = {
        'type': 'object',
        'properties': {
            'user_id': {'type': 'string'},
            'updated_fields': {'type': 'array'},
            'timestamp': {'type': 'string'},
            'event_type': {'type': 'string'}
        },
        'required': ['user_id', 'updated_fields', 'timestamp', 'event_type']
    }

    RECIPE_CREATED = {
        'type': 'object',
        'properties': {
            'recipe_id': {'type': 'string'},
            'author_id': {'type': 'string'},
            'title': {'type': 'string'},
            'timestamp': {'type': 'string'},
            'event_type': {'type': 'string'}
        },
        'required': [
            'recipe_id',
            'author_id',
            'title',
            'timestamp',
            'event_type'
        ]
    }
