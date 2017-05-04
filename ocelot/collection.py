# -*- coding: utf-8 -*-
from collections.abc import MutableSequence, Iterable
import wrapt


class Collection(MutableSequence):
    """A collection of transformation functions is correctly unwrapped by a ``system_model``.

    Useful to quickly specify a list of commonly-grouped functions (e.g. ecospold common data cleanup, economic allocation).

    Instantiate a ``Collection`` with a name, and the desired transformation functions: ``Collection("some name", do_something, do_something_else)``.

    """
    def __init__(self, name, *functions):
        self.name = name
        self.functions = functions
        self.unwrap()

    def unwrap(self):
        self.functions = unwrap_functions(self.functions)

    def __iter__(self):
        return iter(self.functions)

    def __len__(self):
        return len(self.functions)

    def __contains__(self, obj):
        return obj in self.functions

    def __getitem__(self, index):
        return self.functions[index]

    def __setitem__(self, index, obj):
        self.functions[index] = obj

    def insert(self, index, obj):
        self.functions = self.functions[:index] + [obj] + self.functions[index:]

    def __delitem__(self, index):
        del self.functions[index]

    def __reversed__(self):
        for obj in self.functions[::-1]:
            yield obj

    def __call__(self, data):
        for func in self:
            data = func(data)
        return data

    def __str__(self):
        return "Collection {} with {} functions".format(self.name,len(self))

    __repr__ = lambda self: str(self)


def unwrap_functions(lst):
    """Unwrap a list of functions, some of which could themselves be lists of functions."""
    def unwrapper(functions):
        for func in functions:
            # wrapt decorators are iterable for some reason
            if (isinstance(func, Iterable) and
                not isinstance(func, wrapt.FunctionWrapper)):
                for obj in unwrapper(func):
                    yield obj
            else:
                yield func

    return list(unwrapper(lst))
