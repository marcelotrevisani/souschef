import re
from typing import Any, List, Union

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


class GetSetItemMixin:
    def __getitem__(self, item):
        try:
            yaml = self._yaml()
        except TypeError:
            yaml = self._yaml

        recipe_item = yaml.get(item, None)
        if recipe_item is None:
            return None
        return convert_to_abstract_repr(recipe_item, item, yaml)

    def __setitem__(self, key, value):
        try:
            yaml = self._yaml()
        except TypeError:
            yaml = self._yaml
        yaml[key] = value


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
