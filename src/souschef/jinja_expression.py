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


def get_all_jinja_expression(recipe: Recipe):
    for item in recipe:
        if is_jinja_expression(item):
            yield item


def set_global_jinja_var(recipe: Recipe, var_name: str, new_value: Union[str, int]):
    all_jinja_exp = list(get_all_jinja_expression(recipe))
    if not all_jinja_exp:
        recipe.yaml.yaml_set_start_comment("NEW VALUE")
        recipe.yaml.ca.comment[1][0].value = f'#% set {var_name} = "{new_value}" %}}\n'
        return
    for item in all_jinja_exp:
        all_jinja = RE_CHECK_JINJA.split(item.raw_value)
        result = []
        found_var = False
        for single_jinja in all_jinja:
            match_jinja = RE_JINJA_SET_EXPRESSION.match(single_jinja)
            if match_jinja:
                current_var, current_value = match_jinja.groups()
                if current_var == var_name:
                    found_var = True
                    single_jinja = f'#% set {current_var} = "{new_value}" %}}'
            result.append(single_jinja)
        if found_var:
            result = "".join(result)
            result = result.replace("}}#%", "}}\n#%")
            item.raw_value = result.strip()
            return
    all_jinja_exp[-1].raw_value += f'\n#% set {var_name} = "{new_value}" %}}'


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
