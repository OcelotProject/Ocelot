Cutoff system model
*******************

The distinguishing features of the cutoff system model are that waste producers pay the full cost of waste treatment or disposal, and that economic allocation is used to split most multioutput activities.

The cutoff system model consists of a few major steps, each of which is broken up into multiple transformation functions.

Data validation
===============

The first step is to do some basic data validation. We will also do validation for specific types of datasets or specific stages of the system model later on.

.. autofunction:: ocelot.transformations.parameterization.variable_names_are_unique

.. autofunction:: ocelot.transformations.validation.ensure_markets_only_have_one_reference_product

.. autofunction:: ocelot.transformations.validation.ensure_markets_dont_consume_their_ref_product

Data cleanup
============

Variables and formulas
----------------------

Ecospold 2 supports parameterized datasets, where numeric values for exchanges and production volumes can be calculated using a chain for formulas and uncertain parameters. Formulas can be present in four different places (see also the :ref:`dataformat`):

* An exchange in the list ``dataset['exchanges']``.
* A property of an exchange in the list ``dataset['exchanges'][some_index]['properties'][another_index]``. Note that not all exchanges have properties.
* A parameter in the list ``dataset['parameters']``. Again, not all datasets have parameters.
* A technosphere exchange production volume ``dataset['exchanges'][some_index]['production volume']``. Only production exchanges have production volumes.

Across a dataset, the following conventions are used:

* The key ``variable`` gives the name of a variable, e.g. ``{'variable': 'some_name'}``. Variable names must be valid python identifiers, so ``some_name`` instead of ``some name``.
* The key ``formula`` gives a mathematical formula, e.g. ``{'formula': 'some_name * 2'}``.

The Ecospold standard places no real limits on which variables can depend on other variables, so arbitrarily complex relationships are possible.

To make things extra spicy, some variables can be implicit, and instead of being given a name, they are referred to by the id of their containing reference element. So, the formula ``Ref('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')`` means get the numeric value (``amount``) of the exchange whose ``id`` is ``aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee``, and substitute in that amount. Datasets with these implicit variables only occur four times in ecoinvent 3.2 and three times in ecoinvent 3.3. Implicit variables can have three forms:

* ``Ref('some id')``: Get ``amount`` value for exchange *or* parameter with id ``some id``.
* ``Ref('some id', 'ProductionVolume')``: Get production volume for exchange with id ``some id``.
* ``Ref('some id', 'some other id')``: Get ``amount`` for property with id ``some other id`` in exchange ``some id``. This isn't used in ecoinvent 3.2 or 3.3, and isn't supported in the current version of Ocelot.

Our first cleanup function will replace these implicit relationships with named variables.

.. autofunction:: ocelot.transformations.parameterization.implicit_references.replace_implicit_references

Next, we manually fix a couple of known problems in certain formula strings, such as numbers with leading zeros that are not understand by Python.

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

Exchange manipulations
----------------------

We can remove some exchange data which is not used in the cutoff system model.

.. autofunction:: ocelot.transformations.cutoff.cleanup.remove_consequential_exchanges

.. autofunction:: ocelot.transformations.cutoff.cleanup.drop_rp_activity_links

Hard links, or activity links, are links between a consuming and producing activity which exist outside the normal system model linking rules. These links are already included in the undefined datasets, and are specified by dataset authors.

The next function makes sure that we can successfully resolve these hard links in our supply chain graph.

.. autofunction:: ocelot.transformations.activity_links.check_activity_link_validity

We end the manipulation step with two functions related to the treatment of wastes and recyclables.

.. autofunction:: ocelot.transformations.cutoff.wastes.create_recycled_content_datasets

.. autofunction:: ocelot.transformations.cutoff.wastes.flip_non_allocatable_byproducts

Split multioutput activities
============================

Introduction
------------

There are a number of choices to be made when constructing an individual dataset, including what the inputs and outputs of a process are. From a mathematical point of view, the different is simple: inputs have a negative number in the technosphere matrix, while outputs have a postive number. The corresponds to our physical understanding of the system, where inputs are consumed and outputs are produced. However, things are never that simple - for example, in a waste treatment process, it is common to consider the treated waste as an output (with a negative sign), even though it is consumed.

In Ocelot, at least in the current version, we don't make these choices ourselves - the inputs and outputs are defined in the undefined datasets, and our job is instead to handle multioutput datasets so that our constructed technosphere matrix is not singular.

In the undefined datasets, we distinguish between two types of outputs: reference products and byproducts. In general, reference products are the reason that producers do a transforming activity (which is why each dataset must have at least one reference product), and byproducts are what comes along for the ride. However, as with many of the definitions used in LCA, what was a sharp diving line from a distance tends to blur a bit at the boundaries.

We further distinguish three types of products (both reference and byproducts): allocatable, recyclable and waste. Formally, in the internal data format, outputs will have a ``type`` of either ``reference product`` or ``byproduct``, and a ``byproduct classification`` of ``allocatable product``, ``recyclable``, or ``waste``.

Where is the "cutoff" in the cutoff system model?
-------------------------------------------------



In the cutoff approach, the difference between reference products and byproducts lies in how we split multiple outputs of each.

* If we have multiple reference products, we assume that these datasets are parameterized, and we can use the formulas in the different exchanges to split the dataset into multiple datasets with one reference product each.
* If we have multiple byproducts, we use economic allocation to split emissions and inputs between the reference product and the allocatable byproducts.



The first thing to do is to label datasets based on the allocation method that will be used.

.. autofunction:: ocelot.transformations.cutoff.allocation.choose_allocation_method

.. autofunction:: ocelot.transformations.cutoff.economic.economic_allocation

.. autofunction:: ocelot.transformations.cutoff.markets.constrained_market_allocation

.. autofunction:: ocelot.transformations.cutoff.wastes.recycling_allocation

.. autofunction:: ocelot.transformations.cutoff.wastes.waste_treatment_allocation

.. autofunction:: ocelot.transformations.cutoff.combined.combined_production

.. autofunction:: ocelot.transformations.cutoff.combined.combined_production_with_byproducts

Link in space and time
======================

.. autofunction:: ocelot.transformations.locations.relabel_global_to_row

.. autofunction:: ocelot.transformations.cleanup.drop_zero_pv_row_datasets
