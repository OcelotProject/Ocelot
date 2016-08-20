# -*- coding: utf-8 -*-
from .transformations import (
    fix_ecoinvent_parameters,
    variable_names_are_unique,
    relabel_global_to_row,
)


class Configuration(object):
    """This is a dummy class, to be filled in with code that can parse various ways for defining a system model in a list of Python functions, including currying, etc."""
    def __init__(self):
        self.functions = []

    def __iter__(self):
        return iter(self.functions)


# Default config for now is cutoff
default_configuration = [
    variable_names_are_unique,
    fix_ecoinvent_parameters,
    # relabel_global_to_row,
]
