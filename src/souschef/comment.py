import weakref


class Comment:
    def __init__(self, yaml):
        self._yaml = weakref.ref(yaml)
