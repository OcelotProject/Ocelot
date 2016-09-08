.. _space:

Linking consumers and suppliers in space
****************************************

Preparation
===========

Successful linking of datasets requires that the steps be followed in the right order, as they build upon each other.

First, we add the field ``reference product`` to each dataset.

.. autofunction:: ocelot.transformations.utils.label_reference_product

We also need to clean up the data. There are some specific datasets which we can safely modify or delete.

.. autofunction:: ocelot.transformations.locations.markets.delete_allowed_zero_pv_market_datsets

.. autofunction:: ocelot.transformations.locations.markets.assign_fake_pv_to_confidential_datasets

Next, we change global datasets to rest-of-world datasets whenever this is necessary, i.e. whenever there is also a region-specific dataset for this reference product. We need to do this before calculating the attribute-specific uniquely identifying hash, as this hash depends on the location field.

.. autofunction:: ocelot.transformations.locations.rest_of_world.relabel_global_to_row

We then calculate the unique codes from each dataset, which are derived from a number of dataset attributes that together should uniquely identify a dataset.

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

.. autofunction:: ocelot.transformations.locations.markets.allocate_suppliers

Finding consumers
=================

In this section, we link undefined technosphere inputs to the activities that provide these flows. We do this in an iterative fashion - first, find any inputs of cutoff-specific dataset created by the system model. Next, if no provider was found, a suitable regional market is sought. Finally, if no region-specific provider is found, a global supplier will be selected.

.. autofunction:: ocelot.transformations.locations.linking.link_consumers_to_recycled_content_activities

.. autofunction:: ocelot.transformations.locations.linking.link_consumers_to_regional_markets

.. autofunction:: ocelot.transformations.locations.linking.link_consumers_to_global_markets

.. autofunction:: ocelot.transformations.locations.linking.log_and_delete_unlinked_exchanges
