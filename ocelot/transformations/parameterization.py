# -*- coding: utf-8 -*-
from ..collection import Collection
from ..errors import ParameterizationError, IdenticalVariables
from ..io.ecospold2_meta import REFERENCE_REGULAR_EXPRESSIONS
from asteval import Interpreter
from bw2parameters import ParameterSet
import logging
import itertools


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


def iterate_all_parameters(dataset):
    """Generator that returns all parameterized objects in a dataset."""
    for exc in dataset['exchanges']:
        if "variable" in exc or "formula" in exc:
            yield exc
        pv = exc.get("production volume", {})
        if "variable" in pv or "formula" in pv:
            yield pv
        for prop in exc.get('properties', []):
            if "variable" in prop or "formula" in prop:
                yield prop
    for parameter in dataset.get('parameters', []):
        if "variable" in parameter or "formula" in parameter:
            yield parameter


def find_implicit_variables(formula):
    """Find ``Ref(`` implicit variables in ``formula``.

    Returns ``None``, or a dictionary with the following form. All keys are optional, and each list can have multiple values.

    .. code-block:: python

        {
            'exchange': [{'uuid': 'some uuid'}],
            'pv': [{'uuid': 'some uuid'}],
            'property': [{'first': 'some uuid', 'second': 'some uuid'}]
        }

    """
    finder = lambda x: [match.groupdict() for match in x.finditer(formula)]
    found = {key: finder(reg_exp)
             for key, reg_exp in REFERENCE_REGULAR_EXPRESSIONS.items()
             if reg_exp.search(formula)}
    return found or None


class ParameterizedDataset(object):
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

    """
    def __init__(self, dataset):
        self.dataset = dataset
        self.parameters = self.extract_named_parameters(self.dataset)
        self.parameter_set = ParameterSet(self.parameters)

    def extract_named_parameters(self, dataset):
        """Extract named parameters from ``dataset``.

        Each named parameter must have a name, and should have either a numeric value (``amount``) or a ``formula`` string. Parameters without names (``variable``) are not extracted, as don't contribute to dataset recalculation; they only get updated afterwards.

        Returns a dictionary with form: ``{'name': {'amount': number, 'formula': string}}``.

        """
        _ = lambda x: x.strip() if isinstance(x, str) else x
        return {exc['variable']: {key: _(exc[key])
                                  for key in ('amount', 'formula')
                                  if exc.get(key) is not None}
                for exc in iterate_all_parameters(dataset)
                if 'variable' in exc}
        # return self.substitue_references(dataset)

    def find_implicit_variables(self, dataset):
        pass

    def substitute_references(self, dataset):
        pass

    def update_dataset(self):
        # Set up an Interpreter with each variable name and its value
        interpreter = Interpreter()
        for key, value in self.parameter_set.evaluate().items():
            interpreter.symtable[key] = value

        # Update each parameterized exchange
        for exc in iterate_all_parameters(self.dataset):
            if 'formula' in exc:
                exc['amount'] = interpreter(exc['formula'])
            elif 'variable' in exc:
                exc['amount'] = interpreter.symtable[exc['variable']]
            else:
                raise ValueError
        return self.dataset
