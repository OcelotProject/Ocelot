# -*- coding: utf-8 -*-
RC_STRING = ", Recycled Content cut-off"

from ._topology import Topology
topology = Topology()

from ...collection import Collection
from ..utils import label_reference_product
from ..identifying import add_unique_codes
from .linking import (
    actualize_activity_links,
    link_consumers_to_global_markets,
    link_consumers_to_recycled_content_activities,
    link_consumers_to_regional_markets,
    log_unlinked_exchanges,
)
from .markets import (
    add_recycled_content_suppliers_to_markets,
    add_suppliers_to_markets,
    assign_fake_pv_to_confidential_datasets,
    allocate_suppliers,
    delete_allowed_zero_pv_market_datsets,
    delete_suppliers_list,
    update_market_production_volumes,
)
from .market_groups import substitute_market_group_links
from .rest_of_world import relabel_global_to_row, drop_zero_pv_row_datasets
from functools import partial


link_markets_by_pv = Collection(
    label_reference_product,
    delete_allowed_zero_pv_market_datsets,
    assign_fake_pv_to_confidential_datasets,
    relabel_global_to_row,
    add_unique_codes,
    actualize_activity_links,
    add_recycled_content_suppliers_to_markets,
    add_suppliers_to_markets,
    update_market_production_volumes,
    partial(add_suppliers_to_markets, from_type="market activity",
                                      to_type="market group"),
    partial(update_market_production_volumes, kind='market group'),
    allocate_suppliers,
    # delete_suppliers_list,
    # drop_zero_pv_row_datasets,
    link_consumers_to_regional_markets,
    link_consumers_to_recycled_content_activities,
    link_consumers_to_global_markets,
    log_unlinked_exchanges,
    # substitute_market_group_links,  # TODO: Need clever approach
)
