import re
from typing import List, Optional, Union

from ruamel.yaml.comments import CommentedMap, CommentedSeq

from souschef.comment import Comment, comment_factory
from souschef.config import RecipeConfiguration
from souschef.tools import convert_to_abstract_repr


class InlineCommentMixin:
    def _get_yaml_comment(self):
        from souschef.ingredient import Ingredient

        if isinstance(self, Ingredient):
            return self._yaml().ca.items[self._id]
        return self._yaml().ca.comment

    @property
    def inline_comment(self) -> Optional[Comment]:
        try:
            all_comments = self._get_yaml_comment()
            if not all_comments:
                return None
        except (TypeError, AttributeError, IndexError, KeyError):
            return None

        return Comment(all_comments[0], 0) if all_comments[0] else None

    @inline_comment.setter
    def inline_comment(self, comment: str):
        from souschef.ingredient import Ingredient

        try:
            if isinstance(self, Ingredient):
                all_comments = self._yaml().ca.items[self._id][0]
            else:
                all_comments = self._yaml().ca.comment[0]
            if all_comments.value is None:
                raise AttributeError
        except (TypeError, AttributeError, IndexError, KeyError):
            from souschef.ingredient import Ingredient

            if isinstance(self, Ingredient):
                self._yaml().yaml_add_eol_comment(comment, key=self._id, column=0)
            else:
                self._yaml().yaml_add_eol_comment(comment, column=0)
        else:
            list_comments = all_comments.value.split("\n")
            if len(list_comments) <= 1:
                comment = f"# {comment}"
            else:
                list_comments[0] = f"# {comment}"
                comment = "\n".join(list_comments)
            all_comments.value = comment


class SelectorMixin(InlineCommentMixin):
    @property
    def selector(self) -> Optional[str]:
        re_selector = re.compile(r"\s*#\s+\[(.*)\]")
        result = re_selector.search(getattr(self.inline_comment, "raw_value", ""))

        return result.group(1) if result else None

    @selector.setter
    def selector(self, selector_value: str):
        self.inline_comment = f"[{selector_value}]"
        self._get_yaml_comment()[0].value = f" {self._get_yaml_comment()[0].value}"


class ConstrainMixin:
    @property
    def constrain(self) -> str:
        try:
            all_constrains = self._yaml()[self._id].strip().split()[1:]
            return " ".join(all_constrains)
        except (IndexError, AttributeError):
            return ""

    @constrain.setter
    def constrain(self, values: Union[str, List[str]]):
        if isinstance(values, list):
            values = ",".join(values)
        pkg = self._yaml()[self._id].strip().split()[0]
        self._yaml()[self._id] = f"{pkg} {values.strip()}".strip()


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
        yaml = self._get_yaml()

        if isinstance(item, (int, slice)):
            return _get_list_repr(yaml, self._config())[item]

        recipe_item = (
            yaml.get(item, None) if isinstance(yaml, CommentedMap) else yaml[item]
        )
        if recipe_item is None:
            return None
        return convert_to_abstract_repr(recipe_item, item, yaml, self._config())

    def _get_yaml(self):
        try:
            return self._yaml()
        except TypeError:
            return self._yaml

    def __setitem__(self, key, value):
        yaml = self._get_yaml()
        if not isinstance(key, int) or self._config().show_comments:
            yaml[key] = value
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
        yaml[key - num_comments] = value

    def __delitem__(self, key):
        from souschef.comment import Comment

        if isinstance(self[key], Comment):
            self[key].remove()
        else:
            del self._get_yaml()[key]

    def insert(self, index, value):
        from souschef.comment import Comment

        is_comment = re.match(r"^\s*#", value) is not None
        if index < 0:
            index = len(self) + index

        if self._config().show_comments is False:
            self._get_yaml().insert(index, value)
        else:
            pos = max(0, index - 1)
            if is_comment:
                self.__add_comment_to_list(pos, value)
            else:
                self.__add_value_right_position(Comment, index, value)

    def __add_value_right_position(self, Comment, index, value):
        pos_yaml = sum(map(lambda x: not isinstance(x, Comment), self[: index + 1]))

        list_comments = self.__get_all_comments_after_position(Comment, index)

        for p in reversed(range(len(list_comments))):
            del self[index + p]

        self._get_yaml().insert(pos_yaml, value)
        self.__re_add_comments(Comment, list_comments, pos_yaml)

    def __get_all_comments_after_position(self, Comment, index):
        list_comments = []
        for val in self[index:]:
            if isinstance(val, Comment):
                list_comments.append(val.value)
            else:
                break
        return list_comments

    def __re_add_comments(self, Comment, list_comments, pos_yaml):
        comments = f"{Comment.NEW_LINE}".join(list_comments) if list_comments else None
        if list_comments:
            self._get_yaml().yaml_set_comment_before_after_key(
                pos_yaml,
                after=comments,
            )
        if list_comments[-1].strip() == "":
            self[-1].value += f"{Comment.NEW_LINE}{list_comments[-1]}"

    def __add_comment_to_list(self, pos, value):
        if isinstance(self[pos], Comment):
            self[pos].value += f"{Comment.NEW_LINE}{value}"
        else:
            self[pos].inline_comment.value += f"{Comment.NEW_LINE}{value}"


def _get_comment_from_obj(obj_repr):
    try:
        key = obj_repr._id
        try:
            comment = obj_repr._yaml().ca.items[key]
        except KeyError:
            obj_repr._yaml().yaml_add_eol_comment("\n", key=key, column=0)
            comment = obj_repr._yaml().ca.items[key]
            comment[0].value = "\n"
    except AttributeError:
        try:
            ca_obj = obj_repr._yaml()[obj_repr._name]
        except AttributeError:
            ca_obj = obj_repr._yaml()
        if ca_obj.ca.comment is None:
            ca_obj.yaml_add_eol_comment("\n", column=0)
        comment = ca_obj.ca.comment
        comment[0].value = "\n"
    return comment
