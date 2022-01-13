from ruamel.yaml import round_trip_dump

from souschef.recipe import Recipe


def test_change_comment(comment_yaml):
    assert comment_yaml[0].value == "init"
    comment_yaml[0].value = "new comment"
    assert comment_yaml[0].value == "new comment"
    assert comment_yaml[0].raw_value == "# new comment"


def test_change_inline_comment(comment_yaml):
    assert comment_yaml["requirements"].inline_comment == "req inline comment"
    comment_yaml["requirements"].inline_comment.value = "new comment"
    assert comment_yaml["requirements"].inline_comment == "new comment"
    assert comment_yaml["requirements"].inline_comment.value == "new comment"
    assert comment_yaml["requirements"].inline_comment.raw_value == "# new comment"


def test_add_inline_comment(pure_yaml):
    assert pure_yaml["source"].inline_comment is None
    pure_yaml["source"].inline_comment = "inline comment"
    assert pure_yaml["source"].inline_comment == "inline comment"
    assert pure_yaml["source"].inline_comment.value == "inline comment"
    assert pure_yaml["source"].inline_comment.raw_value == " # inline comment"


def test_comment(comment_yaml):
    assert comment_yaml["requirements"].inline_comment.value == "req inline comment"
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


def test_comments_right_after_section(comment_yaml):
    assert comment_yaml["requirements"][0].value == "comment after requirements"
    assert comment_yaml["requirements"]["host"][0].value == "before val1"


def test_comments_right_after_ingredient(comment_yaml):
    assert comment_yaml["requirements"]["host"][2].value == "after val1"


def test_comment_len(comment_yaml):
    assert len(comment_yaml["requirements"].inline_comment) == 18
    assert len(comment_yaml[0]) == 4


def test_inline_comment(path_data, tmpdir):
    recipe = Recipe(load_file=path_data / "without_selector.yaml")
    assert recipe["foo_section"].inline_comment is None
    assert recipe["foo_section"].inline_comment is None

    recipe["foo_section"].inline_comment = "FOO INLINE COMMENT"
    assert recipe["foo_section"].inline_comment == " # FOO INLINE COMMENT"
    recipe["foo_section"].inline_comment = "FOO COMMENT 2"
    assert recipe["foo_section"].inline_comment == "# FOO COMMENT 2"

    assert recipe["foo_section"]["bar_section"][0].inline_comment is None
    recipe["foo_section"]["bar_section"][0].inline_comment = "INLINE VAL1"
    assert recipe["foo_section"]["bar_section"][0].inline_comment == " # INLINE VAL1"

    output_folder = tmpdir.mkdir("inline-comment.yaml-output")
    with open(output_folder / "output_constrain.yaml", "w") as f:
        round_trip_dump(recipe._yaml, f)

    with open(output_folder / "output_constrain.yaml", "r") as f:
        content = f.read()
    assert (
        content
        == """foo_section:  # FOO COMMENT 2
  bar_section:
  - val1  # INLINE VAL1
  - val2
foo_bar: 1
"""
    )


def test_jinja_yaml(simple_full_recipe):
    assert simple_full_recipe[0]
