import re
import weakref
from typing import Any, Iterable, List, MutableSequence, Union

from souschef import mixins
from souschef.config import RecipeConfiguration
from souschef.mixins import _get_list_repr


class Ingredient(mixins.SelectorMixin, mixins.InlineCommentMixin):
    def __init__(self, parent, position):
        self.__yaml = weakref.ref(parent)
        self._id = position

    def __repr__(self) -> str:
        if isinstance(self._id, int):
            return str(self.value)
        return f"{self._id}: {self.value}"

    @property
    def _yaml(self):
        return self.__yaml()

    @property
    def value(self) -> Any:
        if self._id is None:
            return self._yaml
        return self._yaml[self._id]

    @value.setter
    def value(self, val: Any):
        self._yaml[self._id] = val

    def __eq__(self, other) -> bool:
        return self.value == other

    def __contains__(self, item):
        return item in self.value

    @property
    def constrains(self) -> List[str]:
        all_val = re.split(r"\s+", self.value)
        if len(all_val) <= 1:
            return []
        return all_val[1].split(",")

    @constrains.setter
    def constrains(self, value: str):
        self.value = re.sub(r"^(\s*\w+).*", f"\\1  {value}", self.value)

    @property
    def package_name(self):
        return re.split(r"\s+", self.value)[0]

    @package_name.setter
    def package_name(self, value: str):
        self.value = re.sub(r"^(\s*)\w+(.*)", f"\\1{value}\\2", self.value)


class IngredientList(
    mixins.SelectorMixin,
    mixins.InlineCommentMixin,
    mixins.GetSetItemMixin,
    MutableSequence,
):
    def __init__(self, parent_yaml, key: Union[int, str], config: RecipeConfiguration):
        self._key = key
        self._config = weakref.ref(config)
        self.__yaml = weakref.ref(parent_yaml)

    @property
    def _yaml(self):
        return self.__yaml()

    def __repr__(self) -> str:
        return f"{self._key}: {self}"

    def __str__(self) -> str:
        return str(_get_list_repr(self._yaml, self._config()))

    def __eq__(self, other) -> bool:
        if len(other) != len(self):
            return False
        return all(
            ingredient == element
            for ingredient, element in zip(
                _get_list_repr(self._yaml, self._config()), other
            )
        )

    def __iter__(self) -> Iterable:
        return iter(_get_list_repr(self._yaml, self._config()))

    def __contains__(self, item) -> bool:
        return any(
            item in value
            for value in _get_list_repr(self._yaml, self._config())
            if isinstance(value, Ingredient)
        )

    def __len__(self) -> int:
        return len(_get_list_repr(self._yaml, self._config()))

    def append(self, value):
        self.insert(0, value)

    def replace(self, current_value: str, new_value: str):
        for pos, item in enumerate(self):
            if item == current_value:
                self[pos].value = new_value
                break
