"""
Usecase для регистрации пользователей
Расширенная версия с дополнительной валидацией и проверками
"""
from typing import Optional, Dict, Any
import re
from datetime import datetime

from ...schemas.requests import RegisterRequestDTO
from ...schemas.responses import RegisterResponseDTO, UserResponseDTO
from ..base import BaseUsecase, UsecaseResult
from ...infrastructure.common.exceptions import (
    ConflictException,
    ValidationException
)


class RegisterUsecase(BaseUsecase):
    """Usecase для регистрации нового пользователя"""

    def __init__(
        self,
        user_repository,
        security_service,
        **kwargs
    ):
        self.user_repository = user_repository
        self.security_service = security_service
        super().__init__(**kwargs)

    async def execute(self, request: RegisterRequestDTO) -> RegisterResponseDTO:
        """Выполнение регистрации"""
        try:
            # Валидация пользовательских данных
            validation_result = await self.validate_user_data(request.dict())
            if not validation_result["is_valid"]:
                raise ValidationException(
                    f"Ошибки валидации: {', '.join(validation_result['errors'])}")

            # Проверка уникальности email
            email_check = await self.check_email_uniqueness(request.email)
            if not email_check["is_available"]:
                raise ConflictException(
                    f"Email уже используется: {email_check['reason']}")

            # Хеширование пароля
            hashed_password = await self.security_service.hash_password(request.password)

            # Создание пользователя
            user_data = {
                "email": request.email,
                "hashed_password": hashed_password,
                "first_name": request.first_name,
                "last_name": request.last_name,
                "phone": request.phone,
                # Если есть поле username
                "username": getattr(request, 'username', None),
                "role": "user",
                "is_active": True,
                "is_verified": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            user = await self.user_repository.create(user_data)

            # Подготовка ответа
            user_response = UserResponseDTO(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            )

            return RegisterResponseDTO.create_success(
                user_response,
                message=f"Пользователь {user.email} успешно зарегистрирован"
            )

        except Exception as e:
            if isinstance(e, (ConflictException, ValidationException)):
                raise e
            raise ValidationException(f"Ошибка регистрации: {str(e)}")

    async def validate_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Расширенная валидация пользовательских данных
        Мигрировано из старого UserService
        """
        errors = []

        # Валидация email
        email = user_data.get("email", "").strip().lower()
        if not email:
            errors.append("Email является обязательным полем")
        elif not self._is_valid_email(email):
            errors.append("Некорректный формат email")
        elif len(email) > 255:
            errors.append("Email слишком длинный (максимум 255 символов)")

        # Валидация пароля
        password = user_data.get("password", "")
        if not password:
            errors.append("Пароль является обязательным полем")
        elif len(password) < 8:
            errors.append("Пароль должен содержать минимум 8 символов")
        elif len(password) > 128:
            errors.append("Пароль слишком длинный (максимум 128 символов)")
        elif not self._is_strong_password(password):
            errors.append(
                "Пароль должен содержать заглавные и строчные буквы, цифры")

        # Валидация имени
        first_name = user_data.get("first_name", "").strip()
        if not first_name:
            errors.append("Имя является обязательным полем")
        elif len(first_name) < 2:
            errors.append("Имя должно содержать минимум 2 символа")
        elif len(first_name) > 50:
            errors.append("Имя слишком длинное (максимум 50 символов)")
        elif not re.match(r"^[a-zA-Zа-яА-Я\s\-']+$", first_name):
            errors.append("Имя содержит недопустимые символы")

        # Валидация фамилии
        last_name = user_data.get("last_name", "").strip()
        if not last_name:
            errors.append("Фамилия является обязательным полем")
        elif len(last_name) < 2:
            errors.append("Фамилия должна содержать минимум 2 символа")
        elif len(last_name) > 50:
            errors.append("Фамилия слишком длинная (максимум 50 символов)")
        elif not re.match(r"^[a-zA-Zа-яА-Я\s\-']+$", last_name):
            errors.append("Фамилия содержит недопустимые символы")

        # Валидация телефона (опционально)
        phone = user_data.get("phone", "").strip()
        if phone and not self._is_valid_phone(phone):
            errors.append("Некорректный формат телефона")

        # Валидация username (если присутствует)
        username = user_data.get("username", "").strip()
        if username:
            if len(username) < 3:
                errors.append("Username должен содержать минимум 3 символа")
            elif len(username) > 30:
                errors.append(
                    "Username слишком длинный (максимум 30 символов)")
            elif not re.match(r"^[a-zA-Z0-9_]+$", username):
                errors.append(
                    "Username может содержать только буквы, цифры и подчеркивания")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "validated_data": {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "username": username
            }
        }

    async def check_email_uniqueness(self, email: str) -> Dict[str, Any]:
        """
        Расширенная проверка уникальности email
        Мигрировано из старого UserService
        """
        try:
            email = email.strip().lower()

            # Проверяем точное совпадение
            existing_user = await self.user_repository.get_by_email(email)
            if existing_user:
                return {
                    "is_available": False,
                    "reason": "Пользователь с таким email уже существует",
                    "user_id": str(existing_user.id),
                    "user_status": "active" if existing_user.is_active else "inactive"
                }

            # Проверяем похожие email (опционально)
            similar_users = await self.user_repository.get_users_by_email_pattern(email)
            if similar_users:
                return {
                    "is_available": True,
                    "warning": f"Найдены похожие email: {len(similar_users)} пользователей",
                    "similar_count": len(similar_users)
                }

            return {
                "is_available": True,
                "reason": "Email доступен для регистрации"
            }

        except Exception as e:
            return {
                "is_available": False,
                "reason": f"Ошибка проверки email: {str(e)}"
            }

    def _is_valid_email(self, email: str) -> bool:
        """Проверка корректности email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _is_strong_password(self, password: str) -> bool:
        """Проверка надежности пароля"""
        if len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        return has_upper and has_lower and has_digit

    def _is_valid_phone(self, phone: str) -> bool:
        """Проверка корректности телефона"""
        # Удаляем все символы кроме цифр и +
        clean_phone = re.sub(r'[^\d+]', '', phone)

        # Проверяем длину (минимум 10 цифр)
        digit_count = sum(c.isdigit() for c in clean_phone)
        return digit_count >= 10 and digit_count <= 15
