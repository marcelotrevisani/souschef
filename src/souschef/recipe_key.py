import weakref
from typing import Optional, Union

from ruamel.yaml.comments import CommentedMap

from src.souschef.recipe_value import ValueRecipe


class KeyRecipe:
    def __init__(self, name: str, parent: CommentedMap):
        self._parent = weakref.ref(parent)
        pass

    def __repr__(self):
        pass

    @property
    def values(self) -> Union[None, "KeyRecipe", ValueRecipe]:
        return

    @values.setter
    def values(self, items: Union[None, "KeyRecipe", ValueRecipe, str]):
        pass

    @property
    def comment_before(self) -> Optional[str]:
        return None

    @property
    def selector(self) -> Optional[str]:
        return

    @selector.setter
    def selector(self, value: Optional[str]):
        pass

    @comment_before.setter
    def comment_before(self, comment: Optional[str]):
        pass

    @property
    def comment_after(self) -> Optional[str]:
        return None

    @comment_after.setter
    def comment_after(self, comment: Optional[str]):
        pass

    @property
    def comment_inline(self) -> Optional[str]:
        return None

    @comment_inline.setter
    def comment_inline(self, comment: Optional[str]):
        pass
