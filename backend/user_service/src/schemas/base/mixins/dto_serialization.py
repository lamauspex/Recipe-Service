from typing import Optional, Set, Any


class DTOSerializationMixin:
    """
    Миксин с методами сериализации DTO в специфические форматы.

    Предоставляет методы для сериализации в форматы, используемые
    в конкретных сценариях (например, для API ответов, логов и т.д.).
    """

    def to_api_dict(
        self,
        exclude: Optional[Set[str]] = None,
        include: Optional[Set[str]] = None
    ) -> dict[str, Any]:
        """
        Преобразование DTO в словарь для API ответа.

        Может использоваться для исключения чувствительных данных
        или включения только нужных полей.

        Args:
            exclude: Множество имён полей для исключения
            include: Множество имён полей для включения
            (если указано, exclude игнорируется)

        Returns:
            dict[str, Any]: Словарь для API ответа

        Examples:
            >>> user_dto.to_api_dict(exclude={'hashed_password'})
            {'user_name': 'john', 'email': 'john@example.com', ...}
        """
        if include is not None:
            return self.model_dump(
                include=include,
                exclude_none=True
            )
        return self.model_dump(
            exclude=exclude or set(),
            exclude_none=True
        )

    def to_log_dict(
        self,
        sensitive_fields: Optional[Set[str]] = None
    ) -> dict[str, Any]:
        """
        Преобразование DTO в словарь для логирования.

        Автоматически маскирует чувствительные поля.

        Args:
            sensitive_fields: Множество имён чувствительных полей для маскировки

        Returns:
            dict[str, Any]: Словарь для логирования

        Examples:
            >>> user_dto.to_log_dict(sensitive_fields={'hashed_password'})
            {'user_name': 'john', 'hashed_password': '***', ...}
        """
        data = self.model_dump(exclude_none=True)

        if sensitive_fields:
            for field in sensitive_fields:
                if field in data:
                    data[field] = '***'

        return data
