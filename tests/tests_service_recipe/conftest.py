import os
import pytest

os.environ["TESTING"] = "1"
os.environ["RECIPE_SERVICE_TESTING"] = "1"


@pytest.fixture
def valid_title() -> str:
    return "Вкусный борщ"


@pytest.fixture
def short_title() -> str:
    return "Б"


@pytest.fixture
def long_title() -> str:
    return "А" * 200  # > 150 символов


@pytest.fixture
def valid_description() -> str:
    return "Это традиционное блюдо украинской кухни"


@pytest.fixture
def short_description() -> str:
    return "Так"


@pytest.fixture
def mock_recipe_repo():
    """Мок репозитория"""
    from unittest.mock import Mock
    return Mock()
