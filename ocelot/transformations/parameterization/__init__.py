# -*- coding: utf-8 -*-
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
from ...collection import Collection
from .implicit_references import replace_implicit_references
from .known_ecoinvent_issues import fix_known_bad_formula_strings
from .python_compatibility import (
    delete_unparsable_formulas,
    fix_math_formulas,
    lowercase_all_parameters,
    replace_reserved_words,
)
from .recalculation import recalculate
from .validation import variable_names_are_unique

fix_ecoinvent_parameters = Collection(
    replace_implicit_references,
    fix_known_bad_formula_strings,
    fix_math_formulas,
    lowercase_all_parameters,
    replace_reserved_words,
    delete_unparsable_formulas,
)
