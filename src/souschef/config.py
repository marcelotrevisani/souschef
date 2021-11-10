from dataclasses import dataclass

NEW_LINE = "\n"


@dataclass
class RecipeConfiguration:
    show_comments: bool = True
