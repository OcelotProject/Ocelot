# -*- coding: utf-8 -*-
from .locations import relabel_global_to_row
from .parameterization import (
    parameterization_validity_checks,
    parameter_names_are_unique,
)
from .activity_overview import f
from .allocation_method import f

def dummy_transformation(data):
    """This is a dummy transformation that doesn't do anything.

    Used primarily for testing."""
    return data
