# -*- coding: utf-8 -*-
__all__ = (
    "apply_allocation_factors",
    "choose_allocation_method",
    "cleanup_activity_links",
    "cutoff_allocation",
    "economic_allocation",
)

from .allocation import choose_allocation_method, cutoff_allocation
from .economic import economic_allocation
from .utils import apply_allocation_factors
from .wastes import handle_waste_outputs

from ...collection import Collection
from ..activity_links import check_activity_link_validity
from .cleanup import remove_consequential_exchanges, drop_rp_activity_links

cleanup_activity_links = Collection(
    remove_consequential_exchanges,
    drop_rp_activity_links,
    check_activity_link_validity,
)
