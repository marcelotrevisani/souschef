import pytest

from souschef.recipe import Recipe


def test_append_host(comment_yaml):
    comment_yaml["requirements"]["host"].append("NEW_DEPENDENCY")
    assert "NEW_DEPENDENCY" in comment_yaml["requirements"]["host"]


def test_append_complete_recipe(simple_full_recipe):
    simple_full_recipe["requirements"]["host"].append("flit")
    assert "flit" in simple_full_recipe["requirements"]["host"]


@pytest.mark.parametrize("show_comments", (True,))
def test_ingredients_list_insert(comment_yaml, show_comments):
    comment_yaml.show_comments = show_comments
    len_before = len(comment_yaml["requirements"]["host"])
    comment_yaml["requirements"]["host"].insert(0, "NEW_VALUE")
    assert comment_yaml["requirements"]["host"][0] == "NEW_VALUE"
    assert len(comment_yaml["requirements"]["host"]) == len_before + 1

    len_before = len(comment_yaml["requirements"]["host"])
    comment_yaml["requirements"]["host"].insert(1, "SECOND VALUE")
    assert comment_yaml["requirements"]["host"][1] == "SECOND VALUE"
    assert len(comment_yaml["requirements"]["host"]) == len_before + 1

    len_before = len(comment_yaml["requirements"]["host"])
    comment_yaml["requirements"]["host"].insert(8, "THIRD VALUE")
    assert comment_yaml["requirements"]["host"][8] == "THIRD VALUE"
    assert comment_yaml["requirements"]["host"][9] == "# after req"
    assert len(comment_yaml["requirements"]["host"]) == len_before + 1


def test_ingredients_list_insert_comment(comment_yaml):
    comment_yaml.show_comments = True
    comment_yaml["requirements"]["host"].insert(1, "# MY COMMENT")
    assert comment_yaml["requirements"]["host"][1] == "MY COMMENT"

    comment_yaml["requirements"]["host"].insert(1, "# MY COMMENT 2")
    assert comment_yaml["requirements"]["host"][1] == "MY COMMENT 2"


def test_ingredients_list_insert_between_item_comment(comment_yaml):
    comment_yaml["requirements"]["host"].insert(2, "# MY COMMENT")
    assert comment_yaml["requirements"]["host"][2] == "MY COMMENT"


def test_ingredients_list_insert_after_comment(comment_yaml):
    comment_yaml["requirements"]["host"].insert(3, "# MY COMMENT")
    assert comment_yaml["requirements"]["host"][3] == "MY COMMENT"


def test_ingredients_list_insert_comment_between_items(comment_yaml):
    comment_yaml["requirements"]["host"].insert(4, "# MY COMMENT")
    assert comment_yaml["requirements"]["host"][4] == "MY COMMENT"


def test_insert_comment_at_the_end(comment_yaml):
    comment_yaml["requirements"]["host"].insert(-1, "# MY COMMENT")
    assert comment_yaml["requirements"]["host"][-2] == "MY COMMENT"


def test_replace_ingredients_list(comment_yaml):
    assert "val1" in comment_yaml["requirements"]["host"]
    assert "new value 1" not in comment_yaml["requirements"]["host"]

    comment_yaml["requirements"]["host"].replace("val1", "new value 1")
    assert "val1" not in comment_yaml["requirements"]["host"]
    assert "new value 1" in comment_yaml["requirements"]["host"]


def test_ingredient_contains(simple_full_recipe):
    assert any("elmd" in i for i in simple_full_recipe["requirements"]["run"])


def test_list_ingredient_contains(simple_full_recipe):
    assert "elmd" in simple_full_recipe["requirements"]["run"]
    assert "FOOBAR" not in simple_full_recipe["requirements"]["run"]


def test_get_constrains(simple_full_recipe):
    assert simple_full_recipe["requirements"]["run"][0].constrains == "==0.4.8"


def test_set_constrains(simple_full_recipe):
    simple_full_recipe["requirements"]["run"][0].constrains = ">=1.2.3,<2.0.0"
    assert simple_full_recipe["requirements"]["run"][0].constrains == ">=1.2.3,<2.0.0"


def test_get_package_name(simple_full_recipe):
    assert simple_full_recipe["requirements"]["run"][0].package_name == "elmd"
    assert simple_full_recipe["requirements"]["run"][1].package_name == "hdbscan"


def test_set_package_name(simple_full_recipe):
    simple_full_recipe["requirements"]["run"][0].package_name = "pytest"
    assert simple_full_recipe["requirements"]["run"][0].package_name == "pytest"


def test_sort_ingredient_list():
    recipe = Recipe(name="abc")
    recipe["new_sec"] = ["cde", "fgh", "abc"]
    assert sorted(recipe["new_sec"]) == ["abc", "cde", "fgh"]
