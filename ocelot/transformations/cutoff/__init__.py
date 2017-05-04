# -*- coding: utf-8 -*-
__all__ = (
    "apply_allocation_factors",
    "choose_allocation_method",
    "cleanup_activity_links",
    "cutoff_allocation",
    "economic_allocation",
)

RC_STRING = ", Recycled Content cut-off"

from .allocation import choose_allocation_method, cutoff_allocation
from .economic import economic_allocation
from .utils import apply_allocation_factors
from .wastes import handle_waste_outputs, rename_recycled_content_products_after_linking

from ...collection import Collection
from ..activity_links import check_activity_link_validity
from .cleanup import (
    drop_rp_activity_links,
    drop_zero_amount_activity_links,
    remove_consequential_exchanges,
)

cleanup_activity_links = Collection(
<<<<<<< HEAD
    "Cleanup hard (activity) links",
    remove_consequential_exchanges,
=======
>>>>>>> master
    drop_rp_activity_links,
    drop_zero_amount_activity_links,
)
