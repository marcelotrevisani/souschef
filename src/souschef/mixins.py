import re
from collections.abc import Mapping, Sequence
from functools import singledispatchmethod
from typing import List, Optional, Union

from ruamel.yaml.comments import CommentedMap, CommentedSeq

from souschef.comment import Comment, comment_factory
from souschef.config import NEW_LINE, RecipeConfiguration
from souschef.tools import convert_to_abstract_repr, parse_value


class InlineCommentMixin:
    def _get_yaml_comment(self):
        from souschef.ingredient import Ingredient

        if isinstance(self, Ingredient):
            return self.yaml.ca.items[self._id]
        return self.yaml.ca.comment

    @property
    def inline_comment(self) -> Optional[Comment]:
        try:
            all_comments = self._get_yaml_comment()
            if not all_comments:
                return None
        except (TypeError, AttributeError, IndexError, KeyError):
            return None
        if all_comments[0]:
            return Comment(all_comments[0], 0)
        if all_comments[2]:
            return Comment(all_comments[2], 0)

    @inline_comment.setter
    def inline_comment(self, comment: str):
        from souschef.ingredient import Ingredient

        try:
            if isinstance(self, Ingredient):
                all_comments = self.yaml.ca.items[self._id][0]
            else:
                all_comments = self.yaml.ca.comment[0]
            if all_comments.value is None:
                raise AttributeError
        except (TypeError, AttributeError, IndexError, KeyError):
            from souschef.ingredient import Ingredient

            if isinstance(self, Ingredient):
                self.yaml.yaml_add_eol_comment(comment, key=self._id, column=0)
            else:
                self.yaml.yaml_add_eol_comment(comment, column=0)
        else:
            list_comments = all_comments.value.split("\n")
            if len(list_comments) <= 1:
                comment = f"# {comment}"
            else:
                list_comments[0] = f"# {comment}"
                comment = "\n".join(list_comments)
            all_comments.value = comment
        if not self.inline_comment.raw_value.startswith(" "):
            self.inline_comment.raw_value = f" {self.inline_comment.raw_value}"


class SelectorMixin(InlineCommentMixin):
    @property
    def selector(self) -> Optional[str]:
        re_selector = re.compile(r"\s*#\s+\[(.*)\]")
        if not self.inline_comment:
            return None
        result = re_selector.search(self.inline_comment.raw_value)

        return result.groups()[0] if result else None

    @selector.setter
    def selector(self, selector_value: str):
        self.inline_comment = f"[{selector_value}]"


class ConstrainMixin:
    @property
    def constrain(self) -> str:
        try:
            all_constrains = self.yaml[self._id].strip().split()[1:]
            return " ".join(all_constrains)
        except (IndexError, AttributeError):
            return ""

    @constrain.setter
    def constrain(self, values: Union[str, List[str]]):
        if isinstance(values, list):
            values = ",".join(values)
        pkg = self.yaml[self._id].strip().split()[0]
        self.yaml[self._id] = f"{pkg} {values.strip()}".strip()


def _get_elements_and_comments(yaml, config: RecipeConfiguration) -> List:
    if not yaml:
        return []
    result = []
    zip_val = enumerate(yaml) if isinstance(yaml, CommentedSeq) else yaml.items()
    for key, value in zip_val:
        result.append(convert_to_abstract_repr(value, key, yaml, config))
        if config.show_comments is False:
            continue

        comment_token = yaml.ca.items.get(key, None)
        if comment_token is None:
            continue
        if isinstance(value, (CommentedMap, CommentedSeq)):
            result.extend(_get_last_section_comment(yaml, key))
        else:
            list_comment = (
                comment_token[3] if comment_token[2] is None else comment_token[2]
            )
            start_inline = comment_token[2] is not None
            if list_comment is None and comment_token[0]:
                list_comment = comment_token[0]
                start_inline = True
            if not isinstance(list_comment, list):
                list_comment = [list_comment]
            for comment in list_comment:
                result.extend(comment_factory(comment, start_inline))
    return result


def _get_last_section_comment(yaml, key) -> List:
    value = yaml[key]
    if isinstance(value, CommentedMap):
        last_key = next(reversed(value))
        return _get_last_section_comment(value, last_key)
    if isinstance(value, CommentedSeq):
        last_pos = max(len(value) - 1, 0)
        val = value.ca.items.get(last_pos, None)
        try:
            return comment_factory(val[0], True)
        except (AttributeError, IndexError):
            return []
    try:
        val = yaml.ca.items.get(key, None)[2]
        start_inline_comment = not val.value.startswith("\n")
        return comment_factory(val, start_inline_comment)
    except (AttributeError, KeyError, TypeError):
        return []


def _get_list_repr(yaml, config: RecipeConfiguration) -> List:
    result = _get_root_comments(yaml) if config.show_comments else []
    result.extend(_get_elements_and_comments(yaml, config))
    return result


def _get_root_comments(yaml) -> List:
    result = []
    try:
        all_comments = yaml.ca.comment[1]
    except (KeyError, AttributeError, TypeError):
        all_comments = None
    if all_comments is None:
        all_comments = []
        try:
            if yaml.ca.comment[0]:
                comment = yaml.ca.comment[0]
                result.extend(comment_factory(comment, start_inline_comment=True))
        except (KeyError, AttributeError, TypeError):
            pass

    for comment in all_comments:
        result.extend(comment_factory(comment))
    return result


class GetSetItemMixin:
    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return _get_list_repr(self.yaml, self._config())[item]

        recipe_item = (
            self.yaml.get(item, None)
            if isinstance(self.yaml, CommentedMap)
            else self.yaml[item]
        )
        if recipe_item is None:
            return None
        return convert_to_abstract_repr(recipe_item, item, self.yaml, self._config())

    def __setitem__(self, key, value):
        if not isinstance(key, int) or self._config().show_comments:
            if isinstance(value, Mapping):
                self.yaml[key] = CommentedMap()
                for k, v in value.items():
                    self[key][k] = v
            elif isinstance(value, Sequence) and not isinstance(value, str):
                self.yaml[key] = CommentedSeq()
                for i in value:
                    self[key].append(i)
            else:
                pkg_info, comment = parse_value(value)
                self.yaml[key] = pkg_info
                if comment:
                    self[key].inline_comment = comment
            return

        num_comments = 0
        key_pivot = key
        from souschef.comment import Comment

        for item in self:
            if key_pivot == 0:
                break
            if isinstance(item, Comment):
                num_comments += 1
            else:
                key_pivot -= 1
        self.__set_list_val(key - num_comments, value)

    def __set_list_val(self, pos, value):
        if isinstance(value, int) or "#" not in value:
            self.yaml[pos] = value
            return
        self.yaml[pos] = ""
        re_comment = re.match(r"(.*)\s+#(.*)", value)
        if re_comment:
            pkg, comment = re_comment.groups()
            self[pos].inline_comment = comment
            self.yaml[pos] = pkg

    def __delitem__(self, key):
        from souschef.comment import Comment

        if isinstance(self[key], Comment):
            self[key].remove()
        else:
            del self.yaml[key]

    def __insert_value_position(self, index, value):
        pkg_info, selector = parse_value(value)

        if isinstance(index, int):
            self.yaml.insert(index, pkg_info)
        else:
            self.yaml[index] = pkg_info

        if selector:
            self[index].inline_comment = selector

    def insert(self, index, value):
        from souschef.comment import Comment

        is_comment = re.match(r"^\s*#", value) is not None
        if index < 0:
            index = len(self) + index

        if self._config().show_comments is False:
            self.__insert_value_position(index, value)
        else:
            pos = max(0, index - 1)
            if is_comment:
                self.__add_comment_to_list(pos, value)
            else:
                self.__add_value_right_position(Comment, index, value)
        # self[index] = value

    def __add_value_right_position(self, Comment, index, value):
        pos_yaml = sum(map(lambda x: not isinstance(x, Comment), self[: index + 1]))

        list_comments = self.__get_all_comments_after_position(Comment, index)

        for p in reversed(range(len(list_comments))):
            del self[index + p]

        self.__insert_value_position(index, value)
        self.__re_add_comments(list_comments, pos_yaml)

    def __get_all_comments_after_position(self, Comment, index):
        list_comments = []
        for val in self[index:]:
            if isinstance(val, Comment):
                list_comments.append(val.value)
            else:
                break
        return list_comments

    def __re_add_comments(self, list_comments, pos_yaml):
        comments = f"{NEW_LINE}".join(list_comments) if list_comments else None
        if list_comments:
            self.yaml.yaml_set_comment_before_after_key(
                pos_yaml,
                after=comments,
            )
            if list_comments[-1].strip() == "":
                self[-1].value += f"{NEW_LINE}{list_comments[-1]}"

    def __add_comment_to_list(self, pos, value):
        if isinstance(self[pos], Comment):
            self[pos].value += f"{NEW_LINE}{value}"
        else:
            self[pos].inline_comment.value += f"{NEW_LINE}{value}"


def _get_comment_from_obj(obj_repr):
    try:
        key = obj_repr._id
        try:
            comment = obj_repr.yaml.ca.items[key]
        except KeyError:
            obj_repr.yaml.yaml_add_eol_comment("\n", key=key, column=0)
            comment = obj_repr.yaml.ca.items[key]
            comment[0].value = "\n"
    except AttributeError:
        try:
            ca_obj = obj_repr.yaml[obj_repr._name]
        except AttributeError:
            ca_obj = obj_repr.yaml
        if ca_obj.ca.comment is None:
            ca_obj.yaml_add_eol_comment("\n", column=0)
        comment = ca_obj.ca.comment
        comment[0].value = "\n"
    return comment


class AddSection:
    @singledispatchmethod
    def add_section(self, section: dict):
        for key, value in section.items():
            self[key] = value

    @add_section.register
    def add_section_str(self, section: str):
        self.yaml[section] = CommentedMap()
