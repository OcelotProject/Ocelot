# -*- coding: utf-8 -*-
from ..collection import Collection
from ..errors import ParameterizationError


def every_exchange_with_formula_has_a_variable_name(data, logger):
    """Data validity check."""
    for ds in data:
        for exc in ds['exchanges']:
            if 'formula' in exc and 'variable' not in exc:
                raise ParameterizationError
    return data


def parameter_names_are_unique(data, logger):
    """Data validity check."""
    for ds in data:
        if not ds.get('parameters'):
            continue
        if len(ds['parameters']) != len({p['variable'] for p in ds['parameters']}):
            raise ParameterizationError
    return data


parameterization_validity_checks = Collection(
    # every_exchange_with_formula_has_a_variable_name,
    parameter_names_are_unique
)
