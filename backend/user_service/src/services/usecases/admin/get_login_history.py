"""
Usecase для получения истории входов пользователей
"""


from datetime import datetime

from ...dto.requests.login_logging import LoginHistoryRequestDTO
from ...dto.responses.login_monitoring import (
    LoginHistoryResponseDTO,
    LoginHistoryItemDTO
)
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import (
    ValidationException,
    NotFoundException
)


class GetLoginHistoryUsecase(BaseUsecase):
    """Usecase для получения истории входов пользователя"""

    def __init__(
        self,
        login_log_repository,
        user_repository,
        **kwargs
    ):
        self.login_log_repository = login_log_repository
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: LoginHistoryRequestDTO) -> LoginHistoryResponseDTO:
        """Выполнение получения истории входов"""
        try:
            # Валидация входных данных
            if not request.user_id and not request.email:
                raise ValidationException(
                    "Необходимо указать user_id или email")

            # Определяем пользователя
            user = None
            user_id_str = None

            if request.user_id:
                try:
                    from uuid import UUID
                    user_uuid = UUID(request.user_id)
                    user = await self.user_repository.get_by_id(user_uuid)
                except ValueError:
                    raise ValidationException("Некорректный формат user_id")
            elif request.email:
                user = await self.user_repository.get_by_email(request.email)

            if not user:
                raise NotFoundException("Пользователь не найден", "User")

            user_id_str = str(user.id)

            # Получаем историю входов из репозитория логов
            history_data = await self.login_log_repository.get_login_history(
                user_id=user.id,
                email=request.email,
                days=request.days
            )

            # Преобразуем данные в DTO
            history_items = []
            for item in history_data:
                history_item = LoginHistoryItemDTO(
                    timestamp=item.get('timestamp', datetime.utcnow()),
                    ip_address=item.get('ip_address', ''),
                    user_agent=item.get('user_agent'),
                    success=item.get('success', False),
                    failure_reason=item.get('failure_reason')
                )
                history_items.append(history_item)

            # Если нет детальной истории в логах, создаем базовую информацию
            if not history_items:
                # Создаем базовую запись из данных пользователя
                if hasattr(user, 'last_login_at') and user.last_login_at:
                    base_item = LoginHistoryItemDTO(
                        timestamp=user.last_login_at,
                        ip_address=getattr(user, 'last_login_ip', ''),
                        user_agent=getattr(user, 'last_user_agent', None),
                        success=True,
                        failure_reason=None
                    )
                    history_items.append(base_item)

            return LoginHistoryResponseDTO.create_success(
                user_id=user_id_str,
                email=user.email,
                period_days=request.days,
                history=history_items,
                account_created=user.created_at,
                note="История входов получена успешно"
            )

        except Exception as e:
            if isinstance(e, (ValidationException, NotFoundException)):
                raise e
            raise ValidationException("Ошибка получения истории входов") from e
