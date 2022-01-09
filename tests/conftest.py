from pathlib import Path

import pytest

from souschef.recipe import Recipe


@pytest.fixture
def path_data() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="function")
def pure_yaml_with_comments(path_data):
    return Recipe(load_file=path_data / "pure.yaml", show_comments=True)


@pytest.fixture(scope="function")
def pure_yaml(path_data):
    return Recipe(load_file=path_data / "pure.yaml", show_comments=False)


@pytest.fixture(scope="function")
def simple_yaml(path_data):
    return Recipe(load_file=path_data / "simple.yaml")


@pytest.fixture
def comment_yaml(path_data):
    return Recipe(load_file=path_data / "comment.yaml")


@pytest.fixture
def simple_full_recipe(path_data):
    return Recipe(load_file=path_data / "simple_full_recipe.yaml")


@pytest.fixture
def multiple_jinja_var_same_line(path_data):
    return Recipe(load_file=path_data / "multiple_jinja_var_same_line.yaml")
