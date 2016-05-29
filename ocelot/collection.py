from collections.abc import Iterable


class Collection(Iterable):
    """A collection of transform functions is correctly unwrapped by a `SystemModel`.

    Useful to quickly specify a list of commonly-grouped functions (e.g. ecospold common data cleanup, economic allocation).

    """
    def __init__(self, *functions):
        self.functions = functions

    def __iter__(self):
        return iter(self.functions)

    def __len__(self):
        return len(self.functions)
