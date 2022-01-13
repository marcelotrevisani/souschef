from ruamel.yaml import round_trip_dump

from souschef.recipe import Recipe


def test_set_pure_yaml_file(pure_yaml):
    pure_yaml["test"]["requires"].selector = "TESTING SELECTOR"
    assert pure_yaml["test"]["requires"].selector == "TESTING SELECTOR"
    pure_yaml["version"].value = 4
    assert pure_yaml["version"] == 4
    pure_yaml["version"] = 5
    assert pure_yaml["version"] == 5


def test_load_pure_yaml_recipe(pure_yaml):
    assert pure_yaml["test"].selector == "inline test selector"
    assert pure_yaml["version"] == 3
    assert pure_yaml["package"]["name"] == "foo"
    assert pure_yaml["package"]["version"] == "1.0.0"
    assert pure_yaml["test"]["requires"] == ["pip", "pytest"]
    assert len(pure_yaml["test"]["requires"]) == 2
    assert "pip" in pure_yaml["test"]["requires"]
    assert pure_yaml["test"]["commands"] == ["pytest foo"]
    assert pure_yaml["key-extra"] == ["bar"]


def test_create_selector(path_data, tmpdir):
    selector_folder = tmpdir.mkdir("selector-output")
    recipe = Recipe(load_file=path_data / "without_selector.yaml")
    assert recipe["foo_section"].selector is None
    assert recipe["foo_section"]["bar_section"].selector is None
    assert recipe["foo_section"]["bar_section"] == ["val1", "val2"]
    assert recipe["foo_section"]["bar_section"][0].selector is None
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
    assert recipe["requirements"]["host"] == [
        "python >=3.6,<3.9",
        "pip >20.0.0",
        "pytest",
    ]
    recipe["requirements"]["host"][0] = "python"
    recipe["requirements"]["host"][1] = "pip"
    recipe["requirements"]["host"][2] = "pytest <=5.0.1"

    assert recipe["requirements"]["host"] == ["python", "pip", "pytest <=5.0.1"]
    recipe["requirements"]["host"][2].selector = "py2k"

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
  - pytest <=5.0.1  # [py2k]
"""
    )


def test_list_repr_str(comment_yaml):
    comment_yaml.show_comments = True
    assert (
        repr(comment_yaml[-5])
        == "key_without: ['# after key_without - before list', ab, cd,"
        " '# entire section key_without', '']"
    )
    assert (
        str(comment_yaml[-5]) == "['# after key_without - before list', ab, cd,"
        " '# entire section key_without', '']"
    )
    assert comment_yaml[-5][0] == "# after key_without - before list"
    assert comment_yaml[-5][1] == "ab"
    assert comment_yaml[-5][2] == "cd"
    assert comment_yaml[-5] == [
        "# after key_without - before list",
        "ab",
        "cd",
        "# entire section key_without",
        "",
    ]


def test_create_recipe():
    recipe = Recipe(name="my-package", version="1.2.3")
    assert recipe["package"]["version"] == "1.2.3"
    assert recipe["package"]["name"] == "<{ name|lower }}"


def test_check_presence_key(pure_yaml):
    assert "package" in pure_yaml
    assert "abcdef" not in pure_yaml


def test_recipe_keys(comment_yaml):
    assert list(comment_yaml.keys()) == [
        "version",
        "requirements",
        "key_without",
        "other_final",
    ]


def test_recipe_values(simple_yaml):
    assert list(simple_yaml.values()) == [3, "foo", "bar", 1]


def test_iter_as_dict_recipe(simple_yaml):
    assert list(simple_yaml.items()) == [
        ("version", 3),
        ("requirements", "foo"),
        ("key_without", "bar"),
        ("other_final", 1),
    ]


def test_add_section_dict():
    recipe = Recipe(name="my_recipe")
    recipe.add_section(
        {"requirements": {"run": ["numpy", "python"], "host": {"python", "pip"}}}
    )
    assert set(recipe["requirements"]["run"]) == {"numpy", "python"}
    assert set(recipe["requirements"]["host"]) == {"python", "pip"}


def test_add_section_str():
    recipe = Recipe(name="my_recipe")
    assert "NEW_SECTION" not in recipe
    recipe.add_section("NEW_SECTION")
    assert "NEW_SECTION" in set(recipe.keys())

    assert not recipe["NEW_SECTION"].value
    recipe["NEW_SECTION"] = "VALUE FOR NEW_SECTION"
    assert recipe["NEW_SECTION"] == "VALUE FOR NEW_SECTION"


def test_save_recipe(tmp_path):
    recipe_path = tmp_path / "my_recipe.yaml"
    recipe = Recipe(name="my-recipe", version="1.2.3")
    recipe.add_section({"requirements": {"run": ["numpy", "python"]}})
    recipe.add_section({"ABC": "DEF"})
    recipe.save(recipe_path)

    assert recipe_path.is_file()

    loaded_recipe = Recipe(load_file=recipe_path)
    assert "numpy" in loaded_recipe["requirements"]["run"]
    assert loaded_recipe["ABC"] == "DEF"


def test_update_recipe(simple_full_recipe, tmp_path):
    recipe_path = tmp_path / "updated_recipe.yaml"
    simple_full_recipe["requirements"]["host"].append("flit")
    simple_full_recipe.save(recipe_path)

    loaded_recipe = Recipe(load_file=recipe_path)
    assert "flit" in loaded_recipe["requirements"]["host"]
