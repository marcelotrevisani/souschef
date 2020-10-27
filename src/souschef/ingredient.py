import weakref
from typing import Any, Union

from souschef import mixins


class Ingredient(mixins.SelectorMixin, mixins.InlineCommentMixin):
    def __init__(self, parent, position):
        self._yaml = weakref.ref(parent)
        self._id = position

    def __repr__(self) -> str:
        return f"{self._id}: {str(self.value)}"

    @property
    def value(self) -> Any:
        if self._id is None:
            return self._yaml()
        return self._yaml()[self._id]

    @value.setter
    def value(self, val: Any):
        self._yaml()[self._id] = val

    def __eq__(self, other) -> bool:
        return self.value == other


class IngredientList(
    mixins.SelectorMixin, mixins.InlineCommentMixin, mixins.GetSetItemMixin, list
):
    def __init__(self, parent_yaml, key: Union[int, str]):
        self._key = key
        self._yaml = weakref.ref(parent_yaml)

    def __repr__(self) -> str:
        return f"{self._key}: {str(self)}"

    def __str__(self) -> str:
        return str([elem.value for elem in self])

    def __eq__(self, other) -> bool:
        if len(other) != len(self):
            return False
        for ingredient, element in zip(self, other):
            if ingredient != element:
                return False
        return True

    def insert(self, index: int, value: Any) -> None:
        # TODO: test if starts with '#' to be interpreted as a comment
        #  or if it is a Comment
        #  need to analyze if it is the first element to insert the
        #  comment after the last comment of the key
        self._yaml().insert(index, value)
