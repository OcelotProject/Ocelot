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

The first step in data cleanup is to apply the :ref:`generic functions for parameter and formulas <parameterization_cleanup>`.

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

In the cutoff approach, the difference between reference products and byproducts lies in how we split multiple outputs of each.

* If we have multiple reference products, we assume that these datasets are parameterized, and we can use the formulas in the different exchanges to split the dataset into multiple datasets with one reference product each.
* If we have multiple byproducts, we use economic allocation to split emissions and inputs between the reference product and the allocatable byproducts.

The first step in allocation is to label datasets based on the allocation method that will be used.

.. autofunction:: ocelot.transformations.cutoff.allocation.choose_allocation_method

We then apply the allocation functions in order:

.. autofunction:: ocelot.transformations.cutoff.economic.economic_allocation

.. autofunction:: ocelot.transformations.cutoff.markets.constrained_market_allocation

.. autofunction:: ocelot.transformations.cutoff.wastes.recycling_allocation

.. autofunction:: ocelot.transformations.cutoff.wastes.waste_treatment_allocation

.. autofunction:: ocelot.transformations.cutoff.combined.combined_production

.. autofunction:: ocelot.transformations.cutoff.combined.combined_production_with_byproducts

.. autofunction:: ocelot.transformations.cutoff.combined.combined_production_without_products

After allocation, we can drop a category of hard (activity) links - those from a reference product. These hard links don't have any meaning, as reference products are produced by the activity, and don't need to be linked.

.. autofunction:: ocelot.transformations.cutoff.cleanup.drop_rp_activity_links

The next set is :ref:`space`.
