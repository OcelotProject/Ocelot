# -*- coding: utf-8 -*-
from ...io.ecospold2_meta import REFERENCE_REGULAR_EXPRESSIONS
from ..utils import iterate_all_parameters
import itertools
import logging


def get_exchange_reference(formula):
    """Return list of ``(full_reference_strings, uuid)`` from string ``formula``.

    Finds ``Ref(`` implicit variables."""
    re = REFERENCE_REGULAR_EXPRESSIONS['exchange']
    match = re.search(formula)
    if not match:
        return []
    return zip(
        itertools.repeat(match.group(0)),
        [match.group('uuid') for match in re.finditer(formula)]
    )


def get_production_volume_reference(formula):
    """Return list of ``(full_reference_strings, uuid)`` from string ``formula``.

    Finds ``Ref(`` implicit variables."""
    re = REFERENCE_REGULAR_EXPRESSIONS['pv']
    match = re.search(formula)
    if not match:
        return []
    return zip(
        itertools.repeat(match.group(0)),
        [match.group('uuid') for match in re.finditer(formula)]
    )


def find_exchange_or_parameter_by_id(dataset, uuid):
    """Find exchange or parameter in ``dataset`` with id ``uuid``.

    Raises ``ValueError`` if not found in dataset."""
    for exc in dataset['exchanges']:
        if exc['id'] == uuid:
            return exc
    for param in dataset.get('parameters', []):
        if param['id'] == uuid:
            return param
    raise ValueError("Exchange id {} not found in dataset".format(uuid))


def find_production_volume_by_id(dataset, uuid):
    """Find production volume in ``dataset`` with id ``uuid``.

    Raises ``ValueError`` if ``uuid`` not found in dataset, or if the found exchange does not have a production volume."""
    for exc in dataset['exchanges']:
        if exc['id'] == uuid:
            if 'production volume' not in exc:
                raise ValueError("Referenced exchange does not have a prod. volume")
            return exc['production volume']
    raise ValueError("Exchange id {} not found in dataset".format(uuid))


def replace_implicit_references(data):
    """Replace ``Ref(`` with actual variables."""
    for ds in data:
        for obj in iterate_all_parameters(ds):
            if 'formula' not in obj:
                continue

            for string, uuid in get_exchange_reference(obj['formula']):
                reference = find_exchange_or_parameter_by_id(ds, uuid)
                if 'variable' in reference:
                    variable = reference['variable']
                else:
                    # TODO: Check to make sure variable names are unique?
                    variable = "ref_replacement_{}".format(uuid.replace("-", ""))
                    reference['variable'] = variable
                logging.info({
                    'type': 'table element',
                    'data': (ds['name'], string, variable)
                })
                obj['formula'] = obj['formula'].replace(string, variable)

            for string, uuid in get_production_volume_reference(obj['formula']):
                reference = find_production_volume_by_id(ds, uuid)
                if 'variable' in reference:
                    variable = reference['variable']
                else:
                    variable = "ref_pv_replacement_{}".format(uuid.replace("-", ""))
                    reference['variable'] = variable
                logging.info({
                    'type': 'table element',
                    'data': (ds['name'], string, variable)
                })
                obj['formula'] = obj['formula'].replace(string, variable)
    return data

replace_implicit_references.__table__ = {
    'title': 'Replace implicit references like ``Ref("foo")`` with variable names.',
    'columns': ["Activity name", "Reference", "Variable"]
}
