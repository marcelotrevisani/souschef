import pytest

from souschef.recipe import Recipe


def test_add_new_section(pure_yaml):
    assert "abc" not in pure_yaml
    pure_yaml["abc"] = "new section"
    assert pure_yaml["abc"] == "new section"
    assert "abc" in pure_yaml


def test_add_new_section_using_method(pure_yaml):
    assert "new_section" not in pure_yaml
    pure_yaml.add_section({"new_section": "value new section"})

    assert "value new section" == pure_yaml["new_section"]


def test_ingredient_repr(comment_yaml):
    assert repr(comment_yaml["version"]) == "version: 3"


def test_ingredient_str(comment_yaml):
    assert str(comment_yaml["version"]) == "version: 3"


def test_section_value_set_dict(comment_yaml):
    comment_yaml["requirements"] = {"new": 1, "foo": "abc"}
    assert comment_yaml["requirements"]["new"] == 1
    assert comment_yaml["requirements"]["foo"] == "abc"


def test_section_value_set_dict_value(comment_yaml):
    comment_yaml["requirements"].value = {"new": 1, "foo": "abc"}
    assert comment_yaml["requirements"]["new"] == 1
    assert comment_yaml["requirements"]["foo"] == "abc"


def test_section_update(comment_yaml):
    comment_yaml["requirements"].update({"new": 1, "new2": "foobar"})
    assert comment_yaml["requirements"]["new"] == 1
    assert comment_yaml["requirements"]["new2"] == "foobar"


def test_section_update_existing_key(comment_yaml):
    comment_yaml["requirements"].update({"new": 1, "host": "foobar"})
    assert comment_yaml["requirements"]["host"] == "foobar"
    assert comment_yaml["requirements"]["new"] == 1


@pytest.mark.parametrize("value", ("abc", 2, ["a", "b"], True))
def test_section_value_set_str(comment_yaml, value):
    comment_yaml["requirements"] = value
    assert comment_yaml["requirements"] == value


def test_section_repr(comment_yaml):
    assert repr(comment_yaml["requirements"]) == "<Section requirements>"


def test_section_str(comment_yaml):
    assert str(comment_yaml["requirements"]) == "requirements"


def test_section_get_value(pure_yaml):
    assert pure_yaml["package"].value[0] == "foo"
    assert pure_yaml["package"].value[1] == "1.0.0"


def test_section_add_list_with_selectors(pure_yaml):
    # pure_yaml.add_section({"req": {"new": ["python >=3.6 # [win]", "pytest"]}})
    pure_yaml["req"] = {"new": ["python >=3.6 # [win]", "pytest"]}
    assert pure_yaml["req"]["new"][0] == "python >=3.6"
    assert pure_yaml["req"]["new"][0].selector == "win"


def test_section_add_dict_with_selectors(pure_yaml):
    pure_yaml["NEW"] = {"key1": {"key2": "abc  # [win]"}}
    assert pure_yaml["NEW"]["key1"]["key2"].inline_comment == "# [win]"
    assert pure_yaml["NEW"]["key1"]["key2"] == "abc"


def test_add_section_single_value():
    recipe = Recipe("new_recipe")
    recipe["new_section"] = True
    assert recipe["new_section"]


def test_add_section_list_values():
    recipe = Recipe("new_recipe")
    recipe["mult_values"] = ["abc", "def"]
    assert recipe["mult_values"][0] == "abc"
    assert recipe["mult_values"][1] == "def"


def test_add_section_with_constrains():
    recipe = Recipe("new_recipe")
    recipe["sec_sel"] = ["python >=3.6", "pytest"]
    assert recipe["sec_sel"][0].constrains == ">=3.6"


def test_add_section_with_selectors():
    recipe = Recipe("new_recipe")
    recipe["mult_val_sel"] = ["python  # [win]", "pytest"]
    assert not recipe["mult_val_sel"][0].constrains
    assert recipe["mult_val_sel"][0].inline_comment == "# [win]"


def test_add_section_with_selectors_and_constrains():
    recipe = Recipe("new_recipe")
    recipe["sec_sel"] = ["python >=3.6  # [osx]", "pytest"]
    assert recipe["sec_sel"][0].package_name == "python"
    assert recipe["sec_sel"][0].constrains == ">=3.6"
    assert recipe["sec_sel"][0].inline_comment == "# [osx]"


def test_inline_comment_for_section_value(comment_yaml):
    assert comment_yaml["version"]
    assert comment_yaml["version"].inline_comment == "# version inline comment"


def test_add_section_value_and_inline_comment():
    recipe = Recipe("new_recipe")
    recipe["skip"] = 34
    recipe["skip"].inline_comment = "NEW COMMENT"
    assert recipe["skip"] == 34
    assert recipe["skip"].inline_comment == "NEW COMMENT"


def test_iterate_over_section(pure_yaml):
    all_items = list(pure_yaml["test"].items())
    assert all_items == [("requires", ["pip", "pytest"]), ("commands", ["pytest foo"])]


def test_iterate_over_section_keys(pure_yaml):
    assert pure_yaml["test"].keys() == {"requires", "commands"}


def test_iterate_over_section_values(pure_yaml):
    assert list(pure_yaml["test"].values()) == [["pip", "pytest"], ["pytest foo"]]


def test_contains(pure_yaml):
    assert "test" in pure_yaml
    assert "requires" in pure_yaml["test"]
