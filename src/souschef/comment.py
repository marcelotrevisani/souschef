import re
from typing import List

from ruamel.yaml import CommentToken


class Comment:
    NEW_LINE = "\n"

    def __init__(self, yaml, pos: int = 0):
        self._yaml = yaml
        self.__pos = pos

    @property
    def raw_value(self) -> str:
        return self._yaml.value.split(self.NEW_LINE)[self.__pos]

    @raw_value.setter
    def raw_value(self, val: str):
        self.value = val

    @property
    def value(self) -> str:
        all_values = self._yaml.value.split(self.NEW_LINE)
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
        else:
            new_value = re_comment.sub(r"\1" + new_value, self.value)

        all_values = self._yaml.value.split(self.NEW_LINE)
        all_values[self.__pos] = new_value
        self._yaml.value = f"{self.NEW_LINE.join(all_values)}\n"

    def __repr__(self) -> str:
        return self.raw_value

    def __str__(self) -> str:
        return self.value


def comment_factory(
    comment_token: CommentToken, start_inline_comment: bool = False
) -> List[Comment]:
    if comment_token is None:
        return []
    num_lines = max(0, len(comment_token.value.split("\n")) - 1)
    start_pos = 1 if start_inline_comment else 0
    return [Comment(comment_token, pos) for pos in range(start_pos, num_lines)]
