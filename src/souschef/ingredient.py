import re
import weakref
from typing import Any, Iterable, MutableSequence, Union

from souschef import mixins
from souschef.config import RecipeConfiguration
from souschef.mixins import _get_list_repr


class Ingredient(mixins.SelectorMixin, mixins.InlineCommentMixin):
    def __init__(self, parent, position):
        self._yaml = weakref.ref(parent)
        self._id = position

    def __repr__(self) -> str:
        if isinstance(self._id, int):
            return str(self.value)
        return f"{self._id}: {self.value}"

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
    mixins.SelectorMixin,
    mixins.InlineCommentMixin,
    mixins.GetSetItemMixin,
    MutableSequence,
):
    def __init__(self, parent_yaml, key: Union[int, str], config: RecipeConfiguration):
        self._key = key
        self._yaml = weakref.ref(parent_yaml)
        self._config = weakref.ref(config)

    def __repr__(self) -> str:
        return f"{self._key}: {str(self)}"

    def __str__(self) -> str:
        return str(_get_list_repr(self._yaml(), self._config()))

    def __eq__(self, other) -> bool:  # sourcery skip: invert-any-all, use-any
        if len(other) != len(self):
            return False
        for ingredient, element in zip(
            _get_list_repr(self._yaml(), self._config()), other
        ):
            if ingredient != element:
                return False
        return True

    def __iter__(self) -> Iterable:
        return iter(_get_list_repr(self._yaml(), self._config()))

    def __contains__(self, item) -> bool:
        return item in _get_list_repr(self._yaml(), self._config())

    def __len__(self) -> int:
        return len(_get_list_repr(self._yaml(), self._config()))

    def insert(self, index: int, item: Any) -> None:
        # TODO: test if starts with '#' to be interpreted as a comment
        #  or if it is a Comment
        #  need to analyze if it is the first element to insert the
        #  comment after the last comment of the key
        #  check if key right before is a comment or value to see where it is
        #  going to be added
        if index == 0:
            self._yaml().append(item.value)
        elif isinstance(item, str):
            comment = re.search(r"^\s*#", item)
            if comment is not None:
                self._yaml().insert(index, item)
        else:
            from souschef.comment import Comment

            pos = 0
            partial_list = self[:index]
            for val in partial_list:
                if isinstance(val, Comment):
                    continue
                pos += 1
            self._yaml().insert(pos, item)

    def append(self, value):
        self.insert(0, value)
