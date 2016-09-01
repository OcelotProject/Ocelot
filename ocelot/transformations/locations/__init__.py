# -*- coding: utf-8 -*-
from ._topology import Topology

topology = Topology()

from ...collection import Collection
from ..utils import label_reference_product
from ..identifying import add_unique_codes
from .rest_of_world import relabel_global_to_row, drop_zero_pv_row_datasets
from .markets import (
    add_suppliers_to_markets,
    allocate_suppliers,
    delete_suppliers_list,
    link_consumers_to_markets,
    update_market_production_volumes,
)

link_markets = Collection(
    relabel_global_to_row,
    label_reference_product,
    add_unique_codes,
    add_suppliers_to_markets,
    allocate_suppliers,
    update_market_production_volumes,
    delete_suppliers_list,
    drop_zero_pv_row_datasets,
    link_consumers_to_markets,
    # Deal with market groups
)
