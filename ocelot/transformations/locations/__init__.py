# -*- coding: utf-8 -*-
from ._topology import Topology
topology = Topology()

from ..cutoff import RC_STRING
from ...collection import Collection
from ..utils import label_reference_product
from ..identifying import add_unique_codes
from .linking import (
    actualize_activity_links,
    add_reference_product_codes,
    link_consumers_to_global_markets,
    link_consumers_to_recycled_content_activities,
    link_consumers_to_regional_markets,
    log_and_delete_unlinked_exchanges,
)
from .markets import (
    add_recycled_content_suppliers_to_markets,
    add_suppliers_to_markets,
    assign_fake_pv_to_confidential_datasets,
    allocate_all_market_suppliers,
    delete_allowed_zero_pv_market_datsets,
    delete_suppliers_list,
    update_market_production_volumes,
)
from .market_groups import (
    check_markets_only_supply_one_market_group,
    link_market_group_suppliers,
)
from .rest_of_world import relabel_global_to_row, drop_zero_pv_row_datasets
from functools import partial


link_markets = Collection(
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
    allocate_all_market_suppliers,
    link_market_group_suppliers,
    check_markets_only_supply_one_market_group,
    # delete_suppliers_list,
    # drop_zero_pv_row_datasets,
    link_consumers_to_regional_markets,
    link_consumers_to_recycled_content_activities,
    link_consumers_to_global_markets,
    add_reference_product_codes,
    log_and_delete_unlinked_exchanges,
)
