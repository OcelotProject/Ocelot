# -*- coding: utf-8 -*-
from ...collection import Collection
from ...errors import ParameterizationError
from ..utils import iterate_all_parameters
from pprint import pformat


def variable_names_are_unique(data):
    """Variable names must be globally unique within a dataset, including properties, exchanges, production volumes, and parameters.

    Raises ``ParameterizationError`` if duplicates are found."""
    has_variable = lambda x: x.get('variable')

    for ds in data:
        found = set()
        for param in filter(has_variable, iterate_all_parameters(ds)):
            if param['variable'] in found:
                message = "Variable named {} used twice in dataset:\n{}"
                raise ParameterizationError(message.format(param['variable'], ds))
            found.add(param['variable'])
    return data
