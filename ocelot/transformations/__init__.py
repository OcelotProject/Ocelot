# -*- coding: utf-8 -*-
from .locations import relabel_global_to_row
from .parameterization import (
    parameterization_validity_checks,
    parameter_names_are_unique,
)


def dummy_transformation(data, logger):
    """This is a dummy transformation that doesn't do anything.

    Used primarily for testing."""
    return data
