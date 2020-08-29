from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Optional, Union

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from souschef.recipe_key import KeyRecipe
from souschef.recipe_value import ValueRecipe

yaml = YAML(typ="jinja2")
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 600


class Recipe(MutableMapping):
    def __init__(
        self,
        name: Optional[str] = None,
        version: Optional[str] = None,
        load_file: Union[str, Path, None] = None,
    ):
        if load_file:
            self.__yaml = self.__load_recipe(Path(load_file))
        else:
            self.__yaml = self._create_yaml(name, version)

    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        pass

    def __create_yaml(self, name: str, version: Optional[str] = None):
        return yaml.load(
            f'{{% set name = "{name}" %}}\n' f'{{% set version = "{version}" %}}\n'
            if version
            else ""
            "package:\n"
            "    name: {{ name|lower }}\n"
            f'   version: "{version}"\n'
            if version
            else ""
        )

    def __load_recipe(self, path_recipe: Path):
        with open(path_recipe, "r") as yaml_file:
            return yaml.load(yaml_file)

    def __getattr__(self, item) -> Any:
        recipe_item = self.get(item, None)
        if isinstance(recipe_item, CommentedMap):
            return
        if isinstance(recipe_item, CommentedSeq):
            return
        if recipe_item:
            return recipe_item
        return self.get(item.replace("_", "-"), None)

    def __convert_to_abstract_repr(
        self, item: Union[None, CommentedSeq, CommentedMap]
    ) -> Union[None, KeyRecipe, ValueRecipe]:
        if item is None:
            return None
        if isinstance(item, CommentedMap):
            return KeyRecipe(item, parent=self.__yaml)
        if isinstance(item, CommentedSeq):
            return ValueRecipe(item, parent=self.__yaml)
        return item

    def __iter__(self):
        pass

    def __len__(self):
        pass

    def __getitem__(self, item: str):
        if item in self.__yaml:
            return self.__yaml[item]
        raise ValueError(f"Key {item} does not exist.")

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass
