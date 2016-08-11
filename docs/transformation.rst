Transformation functions
************************

Generic validity checks
=======================

.. autofunction:: ocelot.transformations.cleanup.ensure_all_datasets_have_production_volume

.. autofunction:: ocelot.transformations.cleanup.drop_zero_pv_row_datasets

Cleanup known ecoinvent issues
==============================

These cleanup functions are wrapped in the collection ``fix_known_ecoinvent_issues``.

.. autofunction:: ocelot.transformations.known_ecoinvent_issues.fix_formulas

.. autofunction:: ocelot.transformations.known_ecoinvent_issues.fix_clinker_pv_variable_name

.. autofunction:: ocelot.transformations.known_ecoinvent_issues.fix_ethylene_glycol_uses_yield

.. autofunction:: ocelot.transformations.known_ecoinvent_issues.fix_offshore_petroleum_variable_name

.. autofunction:: ocelot.transformations.known_ecoinvent_issues.fix_benzene_chlorination_unit
