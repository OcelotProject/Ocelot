# -*- coding: utf-8 -*-
from ..collection import Collection
from ..wrapper import TransformationWrapper
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
from .validation import (
    ensure_mandatory_properties,
    ensure_production_exchanges_have_production_volume,
    validate_markets,
)

pv_cleanup = Collection(
    ensure_production_exchanges_have_production_volume,
    TransformationWrapper(create_pv_parameters),
)
