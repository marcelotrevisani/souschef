import weakref
from typing import Union

from ruamel.yaml.comments import CommentedMap

from souschef import mixins


class Section(
    mixins.GetSetAttrMixin,
    mixins.SelectorMixin,
    mixins.GetSetItemMixin,
    mixins.InlineCommentMixin,
):
    def __init__(self, name: Union[int, str], item: CommentedMap, parent: CommentedMap):
        self._parent = weakref.ref(parent)
        self._yaml = weakref.ref(item)
        self._name = name

    def __repr__(self) -> str:
        return f"<Section name={self._name}>"

    def __str__(self) -> str:
        return self._name

    @property
    def values(self) -> Union[None, "Section"]:
        return

    @values.setter
    def values(self, items: Union[None, "Section", str]):
        pass
