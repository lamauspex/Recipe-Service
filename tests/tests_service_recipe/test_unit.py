"""
Тесты валидаторов рецептов
"""

from backend.service_recipe.src.schemas.base.validated import (
    TitleValidator,
    DescriptionValidator
)


class TestTitleValidator:
    """Тесты TitleValidator"""

    def test_valid_title_returns_true(self, valid_title: str):
        """Валидное название должно проходить валидацию"""
        is_valid, errors = TitleValidator.validate(valid_title)

        assert is_valid is True
        assert len(errors) == 0

    def test_short_title_returns_false(self, short_title: str):
        """Слишком короткое название должно возвращать ошибку"""
        is_valid, errors = TitleValidator.validate(short_title)

        assert is_valid is False
        assert len(errors) > 0

    def test_long_title_returns_false(self, long_title: str):
        """Слишком длинное название должно возвращать ошибку"""
        is_valid, errors = TitleValidator.validate(long_title)

        assert is_valid is False

    def test_title_with_special_chars_returns_false(self):
        """Название с недопустимыми символами должно возвращать ошибку"""
        is_valid, errors = TitleValidator.validate("Борщ!!!")

        assert is_valid is False

    def test_title_exactly_min_length_returns_true(self):
        """Название ровно минимальной длины (2) должно проходить"""
        is_valid, errors = TitleValidator.validate("Борщ")

        assert is_valid is True

    def test_title_exactly_max_length_returns_true(self):
        """Название ровно максимальной длины (150) должно проходить"""
        is_valid, errors = TitleValidator.validate("А" * 150)

        assert is_valid is True


class TestDescriptionValidator:
    """Тесты DescriptionValidator"""

    def test_valid_description_returns_true(self, valid_description: str):
        """Валидное описание должно проходить валидацию"""
        is_valid, errors = DescriptionValidator.validate(valid_description)

        assert is_valid is True
        assert len(errors) == 0

    def test_short_description_returns_false(self, short_description: str):
        """Слишком короткое описание должно возвращать ошибку"""
        is_valid, errors = DescriptionValidator.validate(short_description)

        assert is_valid is False

    def test_long_description_returns_false(self):
        """Слишком длинное описание должно возвращать ошибку"""
        is_valid, errors = DescriptionValidator.validate("А" * 501)

        assert is_valid is False

    def test_description_exactly_min_length_returns_true(self):
        """Описание ровно минимальной длины (5) должно проходить"""
        is_valid, errors = DescriptionValidator.validate("А" * 10)

        assert is_valid is True

    def test_description_exactly_max_length_returns_true(self):
        """Описание ровно максимальной длины (500) должно проходить"""
        is_valid, errors = DescriptionValidator.validate("А" * 500)

        assert is_valid is True
