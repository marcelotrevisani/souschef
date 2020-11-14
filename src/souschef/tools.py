from typing import Union

from ruamel.yaml.comments import CommentedMap, CommentedSeq


def convert_to_abstract_repr(
    item: Union[None, CommentedSeq, CommentedMap], name: str, yaml, config
):
    from souschef.ingredient import Ingredient
    from souschef.section import Section

    if isinstance(item, CommentedMap):
        return Section(name=name, item=item, parent=yaml, config=config)

    if isinstance(item, CommentedSeq):
        from souschef.ingredient import IngredientList

        return IngredientList(parent_yaml=item, key=name, config=config)

    if isinstance(item, (int, str)):
        return Ingredient(parent=yaml, position=name)
    return item
