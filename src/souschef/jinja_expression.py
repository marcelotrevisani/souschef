import re
from typing import Union

from souschef.comment import Comment
from souschef.recipe import Recipe

RE_CHECK_JINJA = re.compile(r"\s*([#{]\s*%.*?\s*%\s*}?)")
RE_JINJA_SET_EXPRESSION = re.compile(
    r"[#{]\s*%\s+set\s+(\w+)\s*=\s*[\'\"]*(.*?)[\'\"]*\s*%\s*}",
    re.DOTALL | re.IGNORECASE,
)


def is_jinja_expression(recipe_item):
    if isinstance(recipe_item, Comment):
        return RE_CHECK_JINJA.search(recipe_item.raw_value) is not None
    return False


def set_global_jinja_var(recipe: Recipe, var_name: str, new_value: Union[str, int]):
    for item in recipe:
        if not is_jinja_expression(item):
            continue
        all_jinja = RE_CHECK_JINJA.split(item.raw_value)
        result = []
        found_var = False
        for pos, single_jinja in enumerate(all_jinja):
            match_jinja = RE_JINJA_SET_EXPRESSION.match(single_jinja)
            if match_jinja:
                current_var, current_value = match_jinja.groups()
                if current_var == var_name:
                    found_var = True
                    start = "#" if pos == 0 else "{"
                    single_jinja = f'{start}% set {current_var} = "{new_value}" %}}'
            result.append(single_jinja)
        if found_var:
            item.raw_value = "".join(result)
            return
    raise ValueError(
        f"It was not possible to find the requested jinja variable '{var_name}'."
    )


def get_global_jinja_var(recipe: Recipe, var_name: str) -> str:
    for item in recipe:
        if not is_jinja_expression(item):
            continue
        all_jinja = RE_CHECK_JINJA.split(item.raw_value)
        for single_jinja in all_jinja:
            match_jinja = RE_JINJA_SET_EXPRESSION.match(single_jinja)
            if match_jinja:
                current_var, current_value = match_jinja.groups()
                if current_var == var_name:
                    return current_value
    raise ValueError(
        f"It was not possible to find the requested jinja variable '{var_name}'."
    )
