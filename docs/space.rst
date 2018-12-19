.. _space:

Linking consumers and suppliers in space
****************************************

General principles
==================

The linking needed to match consumers and suppliers in space can quickly get deep into the details. If you find yourself getting puzzled, remember these general principles:

#. The input master datasets do not link to a specific provider of a good and service - rather, they say that they need product X in location Y. Ocelot needs to find the supplier(s) which can meet this demand.

   #. There is an exception for direct (activity) links, but as these are already resolved in space we just skip them.

#. Transforming activities, market activities, and market groups are all linked following the same general principles.

#. Suppliers are chosen using one of three GIS relationships, in the following order:

   #. Supplier(s) completely contained within the location of the consumer.
   #. A single regional supplier which completely contains the consumer.
   #. A ``RoW`` supplier (``GLO`` would already have been used in the previous step).

#. A market is for a *product*, not a *technology*. Markets can't overlap.

#. Multiple transforming activities can produce the same product in the same region using different technologies. Technologies are identified by the activity name. Transforming activities for a specific technology and product can't overlap.

#. A market group is supplied only by other markets and market groups. Market groups can overlap.

#. ``RoW`` locations are resolved in space during linking. ``RoW`` is calculated per technology and reference product for transforming activities, and per product for markets. Market groups can't have the ``RoW`` location.

#. The production volumes of markets and market groups are the sum of the production volumes of their suppliers with the same reference product.

#. The production volumes of ``RoW`` datasets are calculated by subtracting the region-specific production volumes, and subtracting from the global production volume. This value is rounded up to zero if necessary.

These general principles have the following side effects:

*. A potential supplier whose location *partially* overlaps a consumer will not meet any of the three GIS relationships, and so will never be chosen as a supplier.
*. The search for suppliers will stop as soon as at least one supplier is found. That means that a large consuming region can be supplied by a single small supplier, if it is the only supplier whose location is completely inside the consuming region.

Preparation
===========

Successful linking of datasets requires that these steps be followed in the right order, as they build upon each other.

First, we add the field ``reference product`` to each dataset.

.. autofunction:: ocelot.transformations.utils.label_reference_product

We also need to clean up the data. There are some specific datasets which we can safely modify or delete.

.. autofunction:: ocelot.transformations.locations.markets.delete_allowed_zero_pv_market_datsets

.. autofunction:: ocelot.transformations.locations.markets.assign_fake_pv_to_confidential_datasets

Next, we change global datasets to rest-of-world datasets whenever there is also a region-specific dataset for this reference product. This is only done on transforming and market activity, but not on market groups.

.. autofunction:: ocelot.transformations.locations.rest_of_world.relabel_global_to_row

Basic data validity check that market groups with ``RoW`` locations are not allowed:

.. autofunction:: ocelot.transformations.market_groups.no_row_market_groups

We then calculate unique codes from each dataset, to identify them easily e.g. when linking. These codes are derived from dataset attributes, including the location field.

.. autofunction:: ocelot.transformations.identifying.add_unique_codes

.. autofunction:: ocelot.transformations.utils.activity_hash

Finding suppliers
=================

In this section, we will fill up market datasets with their inputs. These inputs are not defined in the dataset, but should be filled automatically from other input datasets by matching the name of the market reference product.

Using our new identifying codes, we can turn activity links (hard links that are not resolved by our linking algorithm, but rather specified already in the undefined datasets) from an `UUID <https://en.wikipedia.org/wiki/Universally_unique_identifier>`__ to an actual link with a specific dataset. This can only happen after allocation because the activity link reference could have been to a multi-output dataset which is now split into multiple datasets (which would make the UUID non-unique). Actual linking means that we add the ``code`` attribute to the exchange, and this code refers to the dataset which produces the product that is being consumed.

.. autofunction:: ocelot.transformations.locations.linking.actualize_activity_links

In the cutoff model, we have special recycled content datasets. These need to be found in a separate function.

.. autofunction:: ocelot.transformations.locations.markets.add_recycled_content_suppliers_to_markets

We can then apply the general purpose algorithm for finding suppliers, from transforming activities to market activities.

.. autofunction:: ocelot.transformations.locations.markets.add_suppliers_to_markets

We do the same for market groups, which are broad regional collections of markets.

Markets don't start with production volumes - instead, their production volume is defined by the production volumes of their inputs. We need to add these production volume amounts to markets.

.. autofunction:: ocelot.transformations.locations.markets.update_market_production_volumes

Our ``add_suppliers_to_markets`` function has not allocated *between* the possible suppliers - it has only created the list ``suppliers`` which has these possible suppliers. We then choose *how much* of each possible supplier will contribute to each market, based on the supplier's production volumes.

.. autofunction:: ocelot.transformations.locations.markets.allocate_all_market_suppliers

.. autofunction:: ocelot.transformations.locations.markets.allocate_suppliers

Finding consumers
=================

In this section, we link undefined technosphere inputs to the activities that provide these flows. We do this in an iterative fashion - first, find any inputs of cutoff-specific dataset created by the system model. Next, if no provider was found, a suitable regional market is sought. Finally, if no region-specific provider is found, a global supplier will be selected.

.. autofunction:: ocelot.transformations.locations.linking.link_consumers_to_recycled_content_activities

.. autofunction:: ocelot.transformations.locations.linking.link_consumers_to_regional_markets

.. autofunction:: ocelot.transformations.locations.linking.link_consumers_to_global_markets

.. autofunction:: ocelot.transformations.locations.linking.log_and_delete_unlinked_exchanges
