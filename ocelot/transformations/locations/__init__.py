# -*- coding: utf-8 -*-
from ._topology import Topology

topology = Topology()

from ...collection import Collection
from ..utils import label_reference_product
from ..identifying import add_unique_codes
from .rest_of_world import relabel_global_to_row, drop_zero_pv_row_datasets
from .linking import actualize_activity_links
from .markets import (
    add_suppliers_to_markets,
    allocate_suppliers,
    delete_suppliers_list,
    link_consumers_to_markets,
    update_market_production_volumes,
)
from .market_groups import substitute_market_group_links
from functools import partial


"""The order of market linking is important.

First, we add the field ``reference product`` to each dataset. This transformation function, ``label_reference_product``, will also raise an error if any dataset does not have a single reference product output.

Next, we change global datasets to rest-of-world datasets whenever this is necessary, i.e. whenever there is also a region-specific dataset for this reference product. We need to do this before calculating the attribute-specific identifying hash, as this depends in part on the location field.

We then calculate the unique codes from each dataset, which are derived from a number of dataset attributes that together should uniquely identify a dataset. Again, an error is raised if any two datasets have the same code.

Using our new identifying codes, we can turn activity links from an id to an actual link with a specific dataset. This can only happen now because the activity link reference could have been to a multi-output dataset. Actual linking means that we add the ``code`` attribute to the exchange, and this code refers to the dataset which produces the product that is being consumed.

"""

link_markets = Collection(
    label_reference_product,
    relabel_global_to_row,
    add_unique_codes,
    actualize_activity_links,
    add_suppliers_to_markets,
    update_market_production_volumes,
    partial(add_suppliers_to_markets, from_type="market activity",
                                      to_type="market group"),
    # drop_zero_pv_row_datasets,
    partial(update_market_production_volumes, kind='market group'),
    allocate_suppliers,
    delete_suppliers_list,
    link_consumers_to_markets,
    # substitute_market_group_links,  # TODO: Need clever approach
)
