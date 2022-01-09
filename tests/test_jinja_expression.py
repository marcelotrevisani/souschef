from souschef.jinja_expression import (
    get_global_jinja_var,
    is_jinja_expression,
    set_global_jinja_var,
)


def test_add_jinja_var(pure_yaml_with_comments):
    set_global_jinja_var(pure_yaml_with_comments, "version", "10.9.8")
    assert get_global_jinja_var(pure_yaml_with_comments, "version") == "10.9.8"


def test_is_jinja_expression(simple_full_recipe):
    assert is_jinja_expression(simple_full_recipe[0])
    assert not is_jinja_expression(simple_full_recipe[-1])


def test_get_global_jinja_var(simple_full_recipe):
    assert get_global_jinja_var(simple_full_recipe, "name") == "mat_discover"
    assert get_global_jinja_var(simple_full_recipe, "version") == "1.2.1"


def test_get_global_jinja_var_multiple_one_line(multiple_jinja_var_same_line):
    assert get_global_jinja_var(multiple_jinja_var_same_line, "name") == "mat_discover"
    assert get_global_jinja_var(multiple_jinja_var_same_line, "version") == "1.2.1"


def test_set_global_jinja_var(simple_full_recipe):
    set_global_jinja_var(simple_full_recipe, "name", "NEW_NAME")
    assert get_global_jinja_var(simple_full_recipe, "name") == "NEW_NAME"

    set_global_jinja_var(simple_full_recipe, "version", "3.2.1")
    assert get_global_jinja_var(simple_full_recipe, "version") == "3.2.1"


def test_set_global_jinja_var_multiple_one_line(multiple_jinja_var_same_line):
    set_global_jinja_var(multiple_jinja_var_same_line, "name", "NEW_NAME")
    assert get_global_jinja_var(multiple_jinja_var_same_line, "name") == "NEW_NAME"

    set_global_jinja_var(multiple_jinja_var_same_line, "version", "3.2.1")
    assert get_global_jinja_var(multiple_jinja_var_same_line, "version") == "3.2.1"
