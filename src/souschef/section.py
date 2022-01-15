import weakref
from collections import abc
from typing import Mapping, Union

from ruamel.yaml.comments import CommentedMap, CommentedSeq

from souschef import mixins
from souschef.tools import convert_to_abstract_repr, parse_value


class Section(
    mixins.SelectorMixin,
    mixins.GetSetItemMixin,
    mixins.InlineCommentMixin,
    mixins.AddSection,
):
    def __init__(
        self,
        name: Union[int, str],
        item: CommentedMap,
        parent: CommentedMap,
        config,
    ):
        self.__yaml = weakref.ref(item)
        self._parent = weakref.ref(parent)
        self._config = weakref.ref(config)
        self._name = name

    def __repr__(self) -> str:
        return f"<Section {self._name}>"

    def items(self):
        for k, v in self.yaml.items():
            yield k, convert_to_abstract_repr(v, k, self._parent(), self._config())

    def keys(self):
        return self.yaml.keys()

    def values(self):
        for _, val in self.items():
            yield val

    @property
    def yaml(self):
        return self.__yaml()

    def __str__(self) -> str:
        return self._name

    def __contains__(self, item):
        return item in self.yaml

    @property
    def value(self):
        return [v for v in self]

    @value.setter
    def value(self, items):
        if isinstance(items, abc.Mapping):
            for key, value in items.items():
                self[key] = value
        elif isinstance(items, str):
            pkg_info, comment = parse_value(items)
            self._parent()[self._name] = pkg_info
            self.inline_comment = comment
        elif isinstance(items, abc.Sequence):
            self._parent()[self._name] = CommentedSeq()
            for pos, i in enumerate(items):
                pkg_info, comment = parse_value(i)
                self._parent()[self._name].append(pkg_info)
                if comment:
                    self[pos].inline_comment = comment
        else:
            self._parent()[self._name] = items

    def update(self, section: Mapping):
        for k, val in section.items():
            self[k] = val
