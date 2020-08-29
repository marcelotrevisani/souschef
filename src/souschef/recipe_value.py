from typing import Optional


class ValueRecipe:
    def __init__(self, value: str, parent):
        self._value = value.strip()

    def __repr__(self) -> str:
        return f"ValueRecipe(value={self._value})"

    def __str__(self) -> str:
        result = self._value
        if self.constrain:
            result += f" {self.constrain}"
        if self.selector:
            result += f"  # [{self.selector}]"
        return result

    @property
    def constrain(self) -> Optional[str]:
        return

    @constrain.setter
    def constrain(self, value: Optional[str]):
        pass

    @property
    def selector(self) -> Optional[str]:
        return

    @selector.setter
    def selector(self, value: Optional[str]):
        pass

    @property
    def comment_before(self) -> Optional[str]:
        return None

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
