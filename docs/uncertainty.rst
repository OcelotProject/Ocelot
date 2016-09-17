Uncertainty distributions, parameters, and the Pedigree Matrix
**************************************************************

Variables and formulas
======================

Ecospold 2 supports parameterized datasets, where numeric values for exchanges and production volumes can be calculated using a chain for formulas and variables with uncertainty distributions. Formulas and variables can be present in four different places (see also the :ref:`dataformat`):

* An exchange in the list ``dataset['exchanges']``.
* A property of an exchange in the list ``dataset['exchanges'][some_index]['properties'][another_index]``. Not all exchanges have properties.
* A parameter in the list ``dataset['parameters']``. Again, not all datasets have parameters.
* A technosphere exchange production volume ``dataset['exchanges'][some_index]['production volume']``. Only production exchanges (type ``reference product`` or ``byproduct``) have production volumes.

Conventions and standards
-------------------------

A variable in an exchange, property, parameter, or production volume is defined with the dictionary key ``variable``. The value for this key will be the string name of the variable, e.g. ``{'variable': 'some_name'}``. Variable names must be valid python identifiers, so ``some_name`` instead of ``some name``.

A formula in an exchange, property, parameter, or production volume is defined with the dictionary key ``formula``. The value for this key will be the formula as a string, e.g. ``{'formula': 'some_name * 2'}``.

Variables can be uncertain. If an uncertainty distribution is present in the same object as a variable, and **no formula** is present, then the given uncertainty is the uncertainty distribution for the variable. If a formula and an uncertainty dictionary are present, behaviour is not defined; there are multiple interpretations for this uncertainty distribution, but e.g. ecoinvent is not consistent.

The Ecospold standard places no real limits on which variables can depend on other variables, so arbitrarily complex relationships are possible.

Formulas that have division by zero errors are evaluated to be zero. However, most of these cases will be rewritten during the data cleaning step.

Evaluation of parameterized datasets
------------------------------------

Evaluation of parameterized datasets is done with the `bw2parameters <https://pypi.python.org/pypi/bw2parameters/>`__ library, which in turn relies on `asteval <https://newville.github.io/asteval/>`__.

After making changes in a parameterized dataset, you can use the following utility function to reevaluate all formula and variable values:

.. autofunction:: ocelot.transformations.parameterization.recalculation.recalculate

You may also be interested in this utility function for extracting parameters:

.. autofunction:: ocelot.transformations.parameterization.recalculation.extract_named_parameters

Implicit references
-------------------

To make things extra spicy, some variables can be implicit, and instead of being given a name, they are referred to by the id of their containing reference element. So, the formula ``Ref('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')`` means get the numeric value (``amount``) of the exchange whose ``id`` is ``aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee``, and substitute in that amount. Datasets with these implicit variables only occur four times in ecoinvent 3.2 and three times in ecoinvent 3.3. Implicit variables can have three forms:

* ``Ref('some id')``: Get ``amount`` value for exchange *or* parameter with id ``some id``.
* ``Ref('some id', 'ProductionVolume')``: Get production volume for exchange with id ``some id``.
* ``Ref('some id', 'some other id')``: Get ``amount`` for property with id ``some other id`` in exchange ``some id``. This isn't used in ecoinvent 3.2 or 3.3, and isn't supported in the current version of Ocelot.

A cleanup function will replace these implicit relationships with named variables.

.. autofunction:: ocelot.transformations.parameterization.implicit_references.replace_implicit_references

.. _parameterization_cleanup:

Generic transformations for parameters and formulas
===================================================

After replacing implicit references (see above), we manually fix a couple of known problems in certain formula strings, such as numbers with leading zeros that are not understand by Python.

.. autofunction:: ocelot.transformations.parameterization.known_ecoinvent_issues.fix_known_bad_formula_strings

The Ecospold 2 formula syntax is similar to Python in some ways, but we still need to use several functions to get formulas that Python can understand. Ocelot is still not 100% compatible with the entire Ecospold 2 formula spec.

.. autofunction:: ocelot.transformations.parameterization.python_compatibility.lowercase_all_parameters

.. autofunction:: ocelot.transformations.parameterization.python_compatibility.fix_math_formulas

.. autofunction:: ocelot.transformations.parameterization.python_compatibility.replace_reserved_words

Finally, in cases where we can't fix problems with formulas, we remove them from the dataset.

.. autofunction:: ocelot.transformations.parameterization.python_compatibility.delete_unparsable_formulas

Production volumes
------------------

Production volumes are specified for exchanges which produce reference product and allocatable byproduct flows. These volumes are used only to calculate the contribution of different transforming activities to markets. As such, production volumes are fixed during the evaluation of a system model in Ocelot. In order to stop an evaluation of the datasets formulas and variables from changing the value of the production volume, we move all such parameterization information to a new parameter, outside of the production volume definition.

.. autofunction:: ocelot.transformations.parameterization.production_volumes.create_pv_parameters

Uncertainty distributions
=========================

Each uncertainty distribution in Ocelot is parsed and manipulated using a specific class. However, most of the time it is more convenient to use one of the following generic functions which are not distribution-specific:

.. autofunction:: ocelot.transformations.uncertainty.scale_exchange

.. autofunction:: ocelot.transformations.uncertainty.adjust_pedigree_matrix_time

As each uncertainty distribution class provides the same API, you can also use the ``get_uncertainty_class`` function to get the correct distribution for an exchange, and then call a class method, e.g. for any exchange ``exc``:

.. code-block:: python

    exc = get_uncertainty_class(exc).repair(exc)

Note that this also works on exchanges which don't have an ``uncertainty`` dictionary - the ``NoUncertainty`` class will still do the right thing (which is normally nothing :).

Uncertainty distribution classes
--------------------------------

.. autoclass:: ocelot.transformations.uncertainty.distributions.NoUncertainty
    :members:

.. autoclass:: ocelot.transformations.uncertainty.distributions.Undefined
    :members:

.. autoclass:: ocelot.transformations.uncertainty.distributions.Lognormal
    :members:

.. autoclass:: ocelot.transformations.uncertainty.distributions.Normal
    :members:

.. autoclass:: ocelot.transformations.uncertainty.distributions.Triangular
    :members:

.. autoclass:: ocelot.transformations.uncertainty.distributions.Uniform
    :members:

Pedigree Matrix
===============

Pedigree matrices are stored as dictionaries (see :ref:`the data format <uncertainty_format>`). Currently, Ocelot only adjust the temporal correlation to adjust datasets to the reference year, but other adjustments are possible.

To adjust uncertainty values for a new pedigree matrix, call the method ``recalculate`` for the correct uncertainty distribution, i.e. one of the following:

.. code-block:: python

    # Works always
    get_uncertainty_class(exc).recalculate(exc)
    # If you know the specific distribution
    Lognormal.recalculate(exc)

To adjust the pedigree matrix value for temporal correlation to a given reference year, use the following utility function (which will already recalculate the uncertainty values):

.. autofunction:: ocelot.transformations.uncertainty.adjust_pedigree_matrix_time

Ocelot includes pedigree matrix values for the original pedigree matrix from ecoinvent 2, as well as the revised values from `Empirically based uncertainty factors for the pedigree matrix in ecoinvent <http://link.springer.com/article/10.1007/s11367-013-0670-5>`__. However, there is not yet an API to use these updated factors.
