from pathlib import Path
from typing import Generator, Iterator, Optional, Union

from ruamel.yaml import YAML

from souschef import mixins
from souschef.config import RecipeConfiguration

yaml = YAML(typ="jinja2")
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 600


class Recipe(mixins.GetSetItemMixin, mixins.InlineCommentMixin, mixins.AddSection):
    def __init__(
        self,
        name: Optional[str] = None,
        version: Optional[str] = None,
        load_file: Union[str, Path, None] = None,
        show_comments: bool = True,
    ):
        if load_file:
            self._yaml = self.__load_recipe(Path(load_file))
        else:
            self._yaml = self.__create_yaml(name, version)
        self._path_recipe = load_file
        self.__config = RecipeConfiguration(show_comments=show_comments)

    def _config(self):
        return self.__config

    @property
    def show_comments(self) -> bool:
        return self._config.show_comments

    @show_comments.setter
    def show_comments(self, val: bool):
        self.__config.show_comments = val

    def __repr__(self) -> str:
        return f"{[s for s in self]}"

    def items(self) -> Iterator:
        yield from zip(self.keys(), self.values())

    def __contains__(self, item: str) -> bool:
        return item in list(self.keys())

    def keys(self) -> Generator:
        yield from self.yaml.keys()

    def values(self) -> Generator:
        for section in self.keys():
            yield self[section]

    def __create_yaml(self, name: str, version: Optional[str] = None):
        content = f'{{% set name = "{name}" %}}\n'
        if version:
            content += f'{{% set version = "{version}" %}}\n'
        content += "package:\n    name: {{ name|lower }}\n"
        if version:
            content += f'    version: "{version}"\n'
        return yaml.load(content)

    def __load_recipe(self, path_recipe: Path):
        with open(path_recipe, "r") as yaml_file:
            return yaml.load(yaml_file)

    def save(self, path_file=None):
        path_file = path_file or self._path_recipe
        if path_file is None:
            raise ValueError("Please inform a valid path to export the recipe.")
        with open(path_file, "w") as recipe:
            yaml.dump(self.yaml, recipe)

    @property
    def yaml(self):
        return self._yaml
