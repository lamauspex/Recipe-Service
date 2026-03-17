""" Базовые схемы для переиспользования """


from pydantic import BaseModel, field_validator

from backend.service_recipe.src.schemas.base.validated import TitleValidator


class TitleValidatedModel(BaseModel):
    """ Базовая схема с валидацией имени """

    name_recipe: str

    @field_validator('name_recipe')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Валидация имени"""

        is_valid, errors = TitleValidator.validate(v)

        if not is_valid:
            raise ValueError('. '.join(errors))
        return v
