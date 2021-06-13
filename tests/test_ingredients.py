import pytest


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
