import pytest


def test_add_new_section(pure_yaml):
    assert "abc" not in pure_yaml
    pure_yaml["abc"] = "new section"
    assert pure_yaml["abc"] == "new section"
    assert "abc" in pure_yaml


def test_ingredient_repr(comment_yaml):
    assert repr(comment_yaml["version"]) == "version: 3"


def test_ingredient_str(comment_yaml):
    assert str(comment_yaml["version"]) == "version: 3"


def test_section_value_set_dict(comment_yaml):
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
    comment_yaml["requirements"].value = value
    assert comment_yaml["requirements"] == value


def test_section_repr(comment_yaml):
    assert repr(comment_yaml["requirements"]) == "<Section requirements>"


def test_section_str(comment_yaml):
    assert str(comment_yaml["requirements"]) == "requirements"


def test_section_get_value(pure_yaml):
    assert pure_yaml["package"].value[0] == "foo"
    assert pure_yaml["package"].value[1] == "1.0.0"
