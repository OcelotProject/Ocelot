# -*- coding: utf-8 -*-
from ..collection import Collection
from .activity_links import (
    check_activity_link_validity,
    add_hard_linked_production_volumes,
    manage_activity_links,
)
from .cleanup import ensure_all_datasets_have_production_volume
from .parameterization import (
    create_pv_parameters,
    fix_ecoinvent_parameters,
    recalculate,
    variable_names_are_unique,
)
from .production_volumes import add_pv_to_allocatable_byproducts
from .utils import normalize_reference_production_amount
from .validation import (
    ensure_ids_are_unique,
    ensure_mandatory_properties,
    ensure_production_exchanges_have_production_volume,
    validate_markets,
)

pv_cleanup = Collection(
    ensure_production_exchanges_have_production_volume,
    add_pv_to_allocatable_byproducts,
    create_pv_parameters,
)
