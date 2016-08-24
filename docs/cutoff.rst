Cutoff system model
*******************

The distinguishing features of the cutoff system model are that waste producers pay the full cost of waste treatment or disposal, and that economic allocation is used to split most multioutput activities.

The cutoff system model consists of a few steps, each of which is broken up into multiple transformation functions.

Data validation
===============

.. autofunction:: ocelot.transformations.parameterization.variable_names_are_unique

.. autofunction:: ocelot.transformations.validation.ensure_markets_only_have_one_reference_product

.. autofunction:: ocelot.transformations.validation.ensure_markets_dont_consume_their_ref_product

Data cleanup
============

.. autofunction:: ocelot.transformations.parameterization.implicit_references.replace_implicit_references

.. autofunction:: ocelot.transformations.parameterization.known_ecoinvent_issues.fix_known_bad_formula_strings

.. autofunction:: ocelot.transformations.parameterization.python_compatibility.lowercase_all_parameters

.. autofunction:: ocelot.transformations.parameterization.python_compatibility.fix_math_formulas

.. autofunction:: ocelot.transformations.parameterization.python_compatibility.replace_reserved_words

.. autofunction:: ocelot.transformations.parameterization.python_compatibility.delete_unparsable_formulas

.. autofunction:: ocelot.transformations.cutoff.cleanup.remove_consequential_exchanges

.. autofunction:: ocelot.transformations.cutoff.cleanup.drop_rp_activity_links

.. autofunction:: ocelot.transformations.activity_links.check_activity_link_validity

Split multioutput activities
============================

.. autofunction:: ocelot.transformations.cutoff.allocation.choose_allocation_method

.. autofunction:: ocelot.transformations.cutoff.economic.economic_allocation

.. autofunction:: ocelot.transformations.cutoff.wastes.recycling_allocation

.. autofunction:: ocelot.transformations.cutoff.wastes.waste_treatment_allocation

.. autofunction:: ocelot.transformations.cutoff.wastes.waste_treatment_allocation

.. autofunction:: ocelot.transformations.cutoff.wastes.waste_treatment_allocation

.. autofunction:: ocelot.transformations.cutoff.combined.combined_production

.. autofunction:: ocelot.transformations.cutoff.combined.combined_production_with_byproducts

Link in space and time
======================

.. autofunction:: ocelot.transformations.locations.relabel_global_to_row

.. autofunction:: ocelot.transformations.cleanup.drop_zero_pv_row_datasets
