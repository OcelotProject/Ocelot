# -*- coding: utf-8 -*-
from .locations import relabel_global_to_row
from .cleanup import (
    drop_zero_pv_row_datasets,
    ensure_all_datasets_have_production_volume,
)
from .known_ecoinvent_issues import fix_known_ecoinvent_issues
from .parameterization import (
    parameterization_validity_checks,
    parameter_names_are_unique,
)


def dummy_transformation(data):
    """This is a dummy transformation that doesn't do anything.

    Used primarily for testing."""
    return data
