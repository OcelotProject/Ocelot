# -*- coding: utf-8 -*-
from .transformations import (
    dummy_transformation,
    parameterization_validity_checks,
    relabel_global_to_row,
)


class Configuration(object):
    """This is a dummy class, to be filled in with code that can parse various ways for defining a system model in a list of Python functions, including currying, etc."""
    def __init__(self):
        self.functions = []

    def __iter__(self):
        return iter(self.functions)


# Default config for now is 3.2 cutoff
default_configuration = [
    parameterization_validity_checks,
    relabel_global_to_row,
    dummy_transformation,
]
