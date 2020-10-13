import weakref
from typing import Any

from souschef import mixins


class Ingredient(mixins.SelectorMixin, mixins.InlineCommentMixin):
    def __init__(self, parent, position):
        self._yaml = weakref.ref(parent)
        self._id = position

    def __repr__(self) -> str:
        return str(self.value)

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


class IngredientList(list, mixins.SelectorMixin, mixins.InlineCommentMixin):
    def __init__(self, parent_yaml, *args):
        self._yaml = weakref.ref(parent_yaml)
        super(IngredientList, self).__init__(args)

    def __repr__(self) -> str:
        return str([elem.value for elem in self])

    def __eq__(self, other) -> bool:
        if len(other) != len(self):
            return False
        for ingredient, element in zip(self, other):
            if ingredient != element:
                return False
        return True

    def __setitem__(self, key, value):
        self._yaml()[key] = value
