import pytest
from ruamel.yaml import round_trip_dump

from souschef.recipe import Recipe


def test_load_pure_yaml_recipe(path_data):
    recipe = Recipe(load_file=path_data / "pure.yaml")
    assert recipe["test"].selector == "inline test selector"
    recipe["test"]["requires"].selector = "TESTING SELECTOR"
    assert recipe["test"]["requires"].selector == "TESTING SELECTOR"
    assert recipe["version"] == 3
    recipe["version"].value = 4
    assert recipe["version"] == 4
    recipe["version"] = 5
    assert recipe["version"] == 5
    assert recipe["version"] == 5
    assert recipe["package"]["name"] == "foo"
    assert recipe["package"]["version"] == "1.0.0"
    assert recipe["test"]["requires"] == ["pip", "pytest"]
    assert len(recipe["test"]["requires"]) == 2
    assert "pip" in recipe["test"]["requires"]
    assert recipe["test"]["commands"] == ["pytest foo"]
    assert recipe["key-extra"] == ["bar"]


def test_create_selector(path_data, tmpdir):
    selector_folder = tmpdir.mkdir("selector-output")
    recipe = Recipe(load_file=path_data / "without_selector.yaml")
    assert recipe["foo_section"].selector == ""
    assert recipe["foo_section"]["bar_section"].selector == ""
    assert recipe["foo_section"]["bar_section"] == ["val1", "val2"]
    assert recipe["foo_section"]["bar_section"][0].selector == ""
    recipe["foo_section"]["bar_section"][0].selector = "win"
    assert recipe["foo_section"]["bar_section"][0].selector == "win"
    recipe["foo_section"]["bar_section"][0].selector = "osx"
    assert recipe["foo_section"]["bar_section"][0].selector == "osx"
    assert recipe["foo_bar"] == 1
    recipe["foo_bar"].value = 2
    assert recipe["foo_bar"] == 2
    assert recipe["foo_bar"] == 2
    recipe["foo_bar"] = 3
    assert recipe["foo_bar"] == 3

    recipe["foo_section"].selector = "FOO SELECTOR"
    with open(selector_folder / "output_selector.yaml", "w") as f:
        round_trip_dump(recipe._yaml, f)

    with open(selector_folder / "output_selector.yaml", "r") as f:
        content = f.readlines()
    assert content == [
        "foo_section:  # [FOO SELECTOR]\n",
        "  bar_section:\n",
        "  - val1  # [osx]\n",
        "  - val2\n",
        "foo_bar: 3\n",
    ]


def test_get_set_constrain(path_data, tmpdir):
    recipe = Recipe(load_file=path_data / "constrains.yaml")
    assert recipe.requirements.host == ["python >=3.6,<3.9", "pip >20.0.0", "pytest"]
    recipe.requirements.host[0] = "python"
    recipe.requirements.host[1] = "pip"
    recipe.requirements.host[2] = "pytest <=5.0.1"

    assert recipe.requirements.host == ["python", "pip", "pytest <=5.0.1"]

    constrain_folder = tmpdir.mkdir("constrain-output")
    with open(constrain_folder / "output_constrain.yaml", "w") as f:
        round_trip_dump(recipe._yaml, f)

    with open(constrain_folder / "output_constrain.yaml", "r") as f:
        content = f.read()
    assert (
        content
        == """requirements:
  host:
  - python
  - pip
  - pytest <=5.0.1
"""
    )


def test_inline_comment(path_data, tmpdir):
    recipe = Recipe(load_file=path_data / "without_selector.yaml")
    assert recipe.foo_section.inline_comment == ""
    assert recipe["foo_section"].inline_comment == ""

    recipe["foo_section"].inline_comment = "FOO INLINE COMMENT"
    assert recipe["foo_section"].inline_comment == "# FOO INLINE COMMENT"
    recipe.foo_section.inline_comment = "FOO COMMENT 2"
    assert recipe["foo_section"].inline_comment == "# FOO COMMENT 2"

    assert recipe["foo_section"]["bar_section"][0].inline_comment == ""
    recipe["foo_section"]["bar_section"][0].inline_comment = "INLINE VAL1"
    assert recipe["foo_section"]["bar_section"][0].inline_comment == "# INLINE VAL1"

    output_folder = tmpdir.mkdir("inline-comment.yaml-output")
    with open(output_folder / "output_constrain.yaml", "w") as f:
        round_trip_dump(recipe._yaml, f)

    with open(output_folder / "output_constrain.yaml", "r") as f:
        content = f.read()
    assert (
        content
        == """foo_section: # FOO COMMENT 2
  bar_section:
  - val1 # INLINE VAL1
  - val2
foo_bar: 1
"""
    )


@pytest.fixture
def comment_yaml(path_data):
    return Recipe(load_file=path_data / "comment.yaml")


def test_comments_right_after_section(comment_yaml):
    assert comment_yaml["requirements"][0].value == "comment after requirements"
    assert comment_yaml["requirements"]["host"][0].value == "before val1"


def test_comment(comment_yaml):
    assert comment_yaml[0].raw_value == "# init"
    assert comment_yaml[0].raw_value == "# init"
    assert str(comment_yaml[0]) == "init"
    assert comment_yaml[0].value == "init"
    assert comment_yaml[1].raw_value == "# before version comment"
    assert comment_yaml[2].value == 3
    assert comment_yaml[3].raw_value == "# after version"


def test_delete_comment(comment_yaml):
    assert comment_yaml[0].raw_value == "# init"
    del comment_yaml[0]
    assert comment_yaml[0].raw_value == "# before version comment"


def test_list_repr_str(comment_yaml):
    assert (
        repr(comment_yaml[-5])
        == "key_without: ['# after key_without - before list', 'ab', 'cd']"
    )
    assert str(comment_yaml[-5]) == "['# after key_without - before list', 'ab', 'cd']"
    assert comment_yaml[-5][0] == "# after key_without - before list"
    assert comment_yaml[-5][1] == "ab"
    assert comment_yaml[-5][2] == "cd"
    assert comment_yaml[-5] == ["# after key_without - before list", "ab", "cd"]
