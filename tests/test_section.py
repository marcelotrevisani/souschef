import pytest


def test_add_new_section(pure_yaml):
    assert "abc" not in pure_yaml
    pure_yaml["abc"] = "new section"
    assert pure_yaml["abc"] == "new section"
    assert "abc" in pure_yaml


def test_section_repr(comment_yaml):
    assert repr(comment_yaml["version"]) == "version: 3"


def test_section_str(comment_yaml):
    assert str(comment_yaml["version"]) == "version: 3"


def test_section_value_set_dict(comment_yaml):
    comment_yaml["requirements"].value = {"new": 1, "foo": "abc"}
    assert comment_yaml["requirements"]["new"] == 1
    assert comment_yaml["requirements"]["foo"] == "abc"


@pytest.mark.parametrize("value", ("abc", 2, ["a", "b"], True))
def test_section_value_set_str(comment_yaml, value):
    comment_yaml["requirements"].value = value
    assert comment_yaml["requirements"] == value
