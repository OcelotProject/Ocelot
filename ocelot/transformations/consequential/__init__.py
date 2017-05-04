# -*- coding: utf-8 -*-
from ...collection import Collection
from ..identifying import add_unique_codes
from ..locations import (
    actualize_activity_links,
    add_suppliers_to_markets,
    allocate_all_market_suppliers,
    assign_fake_pv_to_confidential_datasets,
    delete_allowed_zero_pv_market_datsets,
    delete_suppliers_list,
    link_consumers_to_global_markets,
    link_consumers_to_regional_markets,
    log_and_delete_unlinked_exchanges,
    relabel_global_to_row,
    update_market_production_volumes,
)
from ..utils import label_reference_product
from .byproducts import ensure_byproducts_have_alternative_production
from .constrained_markets import (
    delete_activity_links_to_constrained_markets,
    handle_constrained_markets,
)
from .market_linking import prune_suppliers_by_technology_level
from .combined import split_combined_production
from functools import partial


link_markets_by_technology_level = Collection(
    label_reference_product,
    delete_allowed_zero_pv_market_datsets,
    assign_fake_pv_to_confidential_datasets,
    relabel_global_to_row,
    add_unique_codes,
    actualize_activity_links,
    add_suppliers_to_markets,
    prune_suppliers_by_technology_level,
    update_market_production_volumes,
    partial(add_suppliers_to_markets, from_type="market activity",
                                      to_type="market group"),
    partial(update_market_production_volumes, kind='market group'),
    allocate_all_market_suppliers,
    delete_suppliers_list,
    # drop_zero_pv_row_datasets,
    link_consumers_to_regional_markets,
    link_consumers_to_global_markets,
    log_and_delete_unlinked_exchanges,
    # substitute_market_group_links,  # TODO: Need clever approach
)
