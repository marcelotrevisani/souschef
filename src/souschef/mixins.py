import re
from typing import Any, List, Union

from ruamel.yaml.comments import CommentedMap, CommentedSeq

from souschef.comment import comment_factory
from souschef.tools import convert_to_abstract_repr


class InlineCommentMixin:
    def _get_yaml_comment(self):
        from souschef.ingredient import Ingredient

        if isinstance(self, Ingredient):
            return self._yaml().ca.items[self._id]
        return self._yaml().ca.comment

    @property
    def inline_comment(self) -> str:
        try:
            all_comments = self._get_yaml_comment()
            if not all_comments:
                return ""
        except (TypeError, AttributeError, IndexError, KeyError):
            return ""

        all_comments = all_comments[0]
        if not all_comments.value.strip():
            return ""

        all_comments = all_comments.value.split("\n")
        return all_comments[0] if all_comments else ""

    @inline_comment.setter
    def inline_comment(self, comment: str):
        try:
            all_comments = self._yaml().ca.comment[0]
            if all_comments.value is None:
                raise AttributeError
        except (TypeError, AttributeError, IndexError):
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
    def selector(self) -> str:
        re_selector = re.compile(r"\s*#\s+\[(.*)\]")
        result = re_selector.search(self.inline_comment)

        return result.group(1) if result else ""

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


def _get_elements_and_comments(yaml) -> List:
    if not yaml:
        return []
    result = []
    if isinstance(yaml, CommentedSeq):
        zip_val = enumerate(yaml)
    else:
        zip_val = yaml.items()
    for key, value in zip_val:
        result.append(convert_to_abstract_repr(value, key, yaml))
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


def _get_list_repr(yaml) -> List:
    result = _get_root_comments(yaml)
    result.extend(_get_elements_and_comments(yaml))
    return result


def _get_root_comments(yaml) -> List:
    try:
        all_comments = yaml.ca.comment[1]
    except (KeyError, AttributeError, TypeError):
        all_comments = []
    if all_comments is None:
        all_comments = []
    result = []
    for comment in all_comments:
        result.extend(comment_factory(comment))
    return result


class GetSetItemMixin:
    def __getitem__(self, item):
        yaml = self._get_yaml()

        if isinstance(item, int):
            return _get_list_repr(yaml)[item]

        recipe_item = yaml.get(item, None)
        if recipe_item is None:
            return None
        return convert_to_abstract_repr(recipe_item, item, yaml)

    def _get_yaml(self):
        try:
            return self._yaml()
        except TypeError:
            return self._yaml

    def __setitem__(self, key, value):
        yaml = self._get_yaml()
        yaml[key] = value

    def __delitem__(self, key):
        from souschef.comment import Comment

        if isinstance(self[key], Comment):
            self[key].remove()
        else:
            del self._get_yaml()[key]


class GetSetAttrMixin:
    def __getattr__(self, item: str) -> Any:
        try:
            yaml = self._yaml()
        except (TypeError, KeyError):
            yaml = self._yaml
        recipe_item = yaml.get(item, None)
        if recipe_item is None:
            if "_" in item:
                return self.__getattr__(item.replace("_", "-"))
            raise AttributeError(f"Attribute {item} does not exist.")
        return convert_to_abstract_repr(recipe_item, item, yaml)


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
