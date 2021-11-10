import re
from typing import List

from ruamel.yaml import CommentToken

from souschef.config import NEW_LINE


class Comment:
    def __init__(self, yaml, pos: int = 0):
        self._yaml = yaml
        self.__pos = pos

    @property
    def raw_value(self) -> str:
        return self._yaml.value.split(NEW_LINE)[self.__pos]

    @raw_value.setter
    def raw_value(self, val: str):
        self.value = val

    @property
    def value(self) -> str:
        all_values = self._yaml.value.split(NEW_LINE)
        if not all_values:
            return ""
        re_comment = re.search(r"^\s*#\s*(.*)", all_values[self.__pos], re.DOTALL)
        if re_comment is None:
            return all_values[self.__pos]
        try:
            return re_comment.group(1)
        except IndexError:
            return all_values[self.__pos]

    @value.setter
    def value(self, new_value: str):
        re_comment = re.compile(r"^(\s*#\s*)(.*)", re.DOTALL)
        if re_comment.search(new_value) is None:
            new_value = f"# {new_value}"

        all_values = self._yaml.value.split(NEW_LINE)
        all_values = all_values[:-1] if not all_values[-1] else all_values
        all_values[self.__pos] = new_value
        self._yaml.value = f"{NEW_LINE.join(all_values)}\n"

    def remove(self):
        all_values = self._yaml.value.split(NEW_LINE)
        del all_values[self.__pos]
        self._yaml.value = f"{NEW_LINE.join(all_values)}"

    def __repr__(self) -> str:
        return repr(self.raw_value)

    def __str__(self) -> str:
        return str(self.value)

    def __len__(self) -> int:
        return len(str(self))

    def __eq__(self, other: str) -> bool:
        separated_comment = re.search(r"^\s*#\s*(.*)", other)
        if separated_comment is None:
            return self.value == other or self.raw_value == other
        return self.value == separated_comment.group(1)


def comment_factory(
    comment_token: CommentToken, start_inline_comment: bool = False
) -> List[Comment]:
    if comment_token is None:
        return []
    num_lines = max(0, len(comment_token.value.split("\n")) - 1)
    start_pos = 1 if start_inline_comment else 0
    return [Comment(comment_token, pos) for pos in range(start_pos, num_lines)]
