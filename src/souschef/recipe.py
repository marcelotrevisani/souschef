from pathlib import Path
from typing import Optional, Union

from ruamel.yaml import YAML

from souschef import mixins

yaml = YAML(typ="jinja2")
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 600


class Recipe(mixins.GetSetAttrMixin, mixins.GetSetItemMixin, mixins.InlineCommentMixin):
    def __init__(
        self,
        name: Optional[str] = None,
        version: Optional[str] = None,
        load_file: Union[str, Path, None] = None,
    ):
        self._name = name
        if load_file:
            self._yaml = self.__load_recipe(Path(load_file))
        else:
            self._yaml = self.__create_yaml(name, version)

    def __repr__(self) -> str:
        return f"{str([s for s in self])}"

    def __create_yaml(self, name: str, version: Optional[str] = None):
        return yaml.load(
            f'{{% set name = "{name}" %}}\n{{% set version = "{version}" %}}\n'
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
