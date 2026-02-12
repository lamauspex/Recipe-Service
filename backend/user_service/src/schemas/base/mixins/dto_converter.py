""" Миксины для Pydantic DTO """

from typing import Optional, Set, Any


class DTOConverterMixin:
    """
    Миксин с методами конвертации DTO в словари.

    Предоставляет стандартные методы для преобразования Pydantic моделей
    в словари для передачи в репозитории или другие слои приложения.
    """

    def to_repository_dict(
        self,
        exclude: Optional[Set[str]] = None,
        exclude_unset: bool = True
    ) -> dict[str, Any]:
        """
        Преобразование DTO в словарь для передачи в репозиторий.

        По умолчанию исключает None значения и неустановленные поля.
        Это оптимизирует запросы к БД и использует значения по умолчанию.

        Args:
            exclude: Множество имён полей для исключения
            exclude_unset: Исключать ли поля, которые не были установлены

        Returns:
            dict[str, Any]: Словарь с данными

        Examples:
            >>> user_dto.to_repository_dict()
            {'user_name': 'john',
            'email': 'john@example.com', ...}

            >>> user_dto.to_repository_dict(
                exclude={'created_at', 'updated_at'})
            {'user_name': 'john',
            'email': 'john@example.com', ...}
        """
        return self.model_dump(
            exclude_none=True,
            exclude_unset=exclude_unset,
            exclude=exclude or set()
        )

    def to_model_dict(
        self,
        exclude: Optional[Set[str]] = None,
        exclude_none: bool = False
    ) -> dict[str, Any]:
        """
        Полное преобразование DTO в словарь.

        Включает все поля, включая None значения.
        Используется, когда нужно сохранить полное состояние DTO.

        Args:
            exclude: Множество имён полей для исключения
            exclude_none: Исключать ли None значения

        Returns:
            dict[str, Any]: Полный словарь со всеми полями

        Examples:
            >>> user_dto.to_model_dict()
            {'user_name': 'john',
            'email': 'john@example.com',
            'full_name': None,
            ...}

            >>> user_dto.to_model_dict(exclude={'password'})
            {'user_name': 'john',
            'email': 'john@example.com',
            ...}
        """
        return self.model_dump(
            exclude_none=exclude_none,
            exclude=exclude or set()
        )

    def to_json(
        self,
        exclude: Optional[Set[str]] = None,
        exclude_none: bool = True,
        by_alias: bool = False
    ) -> str:
        """
        Преобразование DTO в JSON строку.

        Удобно для логирования, отправки по сети и т.д.

        Args:
            exclude: Множество имён полей для исключения
            exclude_none: Исключать ли None значения
            by_alias: Использовать ли псевдонимы полей

        Returns:
            str: JSON строка

        Examples:
            >>> user_dto.to_json()
            '{"user_name": "john",
            "email": "john@example.com"}'
        """
        return self.model_dump_json(
            exclude_none=exclude_none,
            exclude=exclude or set(),
            by_alias=by_alias
        )
