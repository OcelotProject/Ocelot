# -*- coding: utf-8 -*-
from ..collection import Collection
from ..errors import ParameterizationError, IdenticalVariables
from ..io.ecospold2_meta import REFERENCE_REGULAR_EXPRESSIONS
from .utils import iterate_all_parameters
from asteval import Interpreter
from bw2parameters import ParameterSet
import itertools
import logging


def every_exchange_with_formula_has_a_variable_name(data):
    """Data validity check."""
    for ds in data:
        for exc in ds['exchanges']:
            if 'formula' in exc and 'variable' not in exc:
                raise ParameterizationError
    return data


def parameter_names_are_unique(data):
    """Data validity check."""
    for ds in data:
        if not ds.get('parameters'):
            continue
        if len(ds['parameters']) != len({p['variable'] for p in ds['parameters']}):
            raise ParameterizationError
    return data


parameterization_validity_checks = Collection(
    # every_exchange_with_formula_has_a_variable_name,
    # parameter_names_are_unique
)


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
                obj['formula'] = obj['formula'].replace(string, variable)

            for string, uuid in get_production_volume_reference(obj['formula']):
                reference = find_production_volume_by_id(ds, uuid)
                if 'variable' in reference:
                    variable = reference['variable']
                else:
                    variable = "ref_pv_replacement_{}".format(uuid.replace("-", ""))
                    reference['variable'] = variable
                obj['formula'] = obj['formula'].replace(string, variable)
    return data


class ParameterizedDataset:
    """Datasets can be parameterized in several ways. This class extracts all the relevant variables and parameters for a dataset, and provides methods to manipulate them.

    Across a dataset, the following conventions are used:

    * The key ``variable`` gives the name of a variable, e.g. ``{'variable': 'some_name'}``. Variable names must be valid python identifiers, so ``some_name`` instead of ``some name``.
    * The key ``formula`` gives a mathematical formula, e.g. ``{'formula': 'some_name * 2'}``.

    Parameters can occur in the following locations (see also the `internal data format description <https://docs.ocelot.space/data_format.html>`)__:

    * An exchange in the list ``dataset['exchanges']``.
    * A property in the list ``dataset['exchanges'][some_index]['properties']``. Not all exchanges have properties.
    * A parameter in the list ``dataset['parameters']``. Not all datasets have parameters.
    * A technosphere exchange production volume ``dataset['exchanges'][some_index]['production volume']``. Only production exchanges have production volumes.

    To make things extra spicy, some variables can be implicit, and referred to by the id of their containing element. So, the formula ``Ref('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')`` means get the numeric value (``amount``) of the exchange whose ``id`` is ``aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee``, and substitute in that amount. Datasets with these implicit variables only occur four times in ecoinvent 3.2 and three times in ecoinvent 3.3. Implicit variables can have three forms:

    * ``Ref('some id')``: Get ``amount`` value for exchange or parameter with id ``some id``.
    * ``Ref('some id', 'ProductionVolume')``: Get production volume for exchange with id ``some id``.
    * ``Ref('some id', 'some other id')``: Get ``amount`` for property with id ``some other id`` in exchange ``some id``. This isn't used in ecoinvent 3.2 or 3.3, and isn't supported here.

    These implicit references should be substituted by the function ``replace_implicit_references`` before this class is used.

    """
    pass


def extract_named_parameters(dataset):
    """Extract named parameters from ``dataset``.

    Each named parameter must have a name, and should have either a numeric value (``amount``) or a ``formula`` string. Parameters without names (``variable``) are not extracted, as don't contribute to dataset recalculation; they only get updated afterwards.

    Returns a dictionary with form: ``{'name': {'amount': number, 'formula': string}}``.

    """
    return {exc['variable']: {key: exc[key]
                              for key in ('amount', 'formula')
                              if exc.get(key) is not None}
            for exc in iterate_all_parameters(dataset)
            if 'variable' in exc}


def recalculate(dataset):
    # Set up an Interpreter with each variable name and its value
    interpreter = Interpreter()
    parameter_set = ParameterSet(extract_named_parameters(dataset))
    for key, value in parameter_set.evaluate().items():
        interpreter.symtable[key] = value

    # Update each parameterized exchange
    for exc in iterate_all_parameters(dataset):
        if 'formula' in exc:
            exc['amount'] = interpreter(exc['formula'])
        elif 'variable' in exc:
            exc['amount'] = interpreter.symtable[exc['variable']]
        else:
            raise ValueError
    return dataset
