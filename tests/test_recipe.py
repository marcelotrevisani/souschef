from souschef import Recipe


def test_load_pure_yaml_recipe(path_data):
    recipe = Recipe(load_file=path_data / "pure.yaml")
    assert recipe.version == 3
    assert recipe["version"] == 3
    assert recipe.package.name == "foo"
    assert recipe.package.version == "1.0.0"
    assert recipe.test.requires == ["pip", "pytest"]
    assert recipe.test.commands == ["pytest foo"]
    assert recipe.key_extra == ["bar"]
