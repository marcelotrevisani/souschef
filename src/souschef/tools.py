import re
from functools import singledispatch
from typing import Union

from ruamel.yaml.comments import CommentedMap, CommentedSeq

from souschef.config import RecipeConfiguration


@singledispatch
def convert_to_abstract_repr(
    item: Union[None, CommentedSeq, CommentedMap],
    name: str,
    yaml,
    config: RecipeConfiguration,
):
    return item


@convert_to_abstract_repr.register
def convert_to_abstract_repr_commented_map(
    item: CommentedMap, name: str, yaml, config: RecipeConfiguration
):
    from souschef.section import Section

    return Section(name=name, item=item, parent=yaml, config=config)


@convert_to_abstract_repr.register
def convert_to_abstract_repr_commented_seq(
    item: CommentedSeq, name: str, yaml, config: RecipeConfiguration
):
    from souschef.ingredient import IngredientList

    return IngredientList(parent_yaml=item, key=name, config=config)


@convert_to_abstract_repr.register
def convert_to_abstract_repr_str(
    item: str, name: str, yaml, config: RecipeConfiguration
):
    from souschef.ingredient import Ingredient

    return Ingredient(parent=yaml, position=name)


@convert_to_abstract_repr.register
def convert_to_abstract_repr_int(
    item: int, name: str, yaml, config: RecipeConfiguration
):
    from souschef.ingredient import Ingredient

    return Ingredient(parent=yaml, position=name)


def parse_value(value):
    selector = ""
    if isinstance(value, str) and "#" in value:
        re_match = re.match(r"(.*?)\s*#(.*)", value)
        value, selector = re_match.groups()
    return value, selector
