# -*- coding: utf-8 -*-
from ... import toolz
from ...data_helpers import reference_products_as_string, production_volume
from ..utils import activity_grouper, get_single_reference_product
from .validation import check_single_global_dataset
import logging

logger = logging.getLogger('ocelot')
detailed = logging.getLogger('ocelot-detailed')


def relabel_global_to_row(data):
    """Change ``GLO`` locations to ``RoW`` if there are region-specific datasets in the activity group.

    Skips market groups, where overlaps are allowed and ``RoW`` is forbidden.

    In addition to relabeling the location field, adjust the production production volume of the ``RoW`` activity by subtracting region-specific production volumes."""
    # Group by (activity name, sorted list of products)
    for key, group in toolz.groupby(activity_grouper, data).items():
        if group and group[0]["type"] == "market group":
            continue
        elif len(group) > 1 and any(ds['location'] == 'GLO' for ds in group):
            check_single_global_dataset(group)
            glo = next(ds for ds in group if ds['location'] == 'GLO')
            region_specific_pv = sum(
                production_volume(obj, 0)
                for obj in group
                if obj != glo
            )
            rp = get_single_reference_product(glo)
            original = production_volume(glo)
            rp['production volume']['amount'] = max(
                rp['production volume']['amount'] - region_specific_pv,
                0
            )
            glo['location'] = 'RoW'

            logger.info({
                'type': 'table element',
                # key is activity name and list of reference products
                'data': (key[0], "; ".join(sorted(key[1])))
            })
            message = ("Created RoW dataset '{}' with PV {:.4g} {} "
                       "(Originally: {:.4g}, minus region-specific: {:.4g})")
            detailed.info({
                'ds': glo,
                'message': message.format(
                    glo['name'],
                    rp['production volume']['amount'],
                    rp['unit'],
                    original,
                    region_specific_pv
                ),
                'function': 'relabel_global_to_row'
            })
        else:
            # Single global dataset - do nothing
            pass
    return data

relabel_global_to_row.__table__ = {
    'title': 'Activities changed from `GLO` to `RoW`',
    'columns': ["Name", "Product(s)"]
}


def drop_zero_pv_row_datasets(data):
    """Drop datasets which have the location ``RoW`` and zero production volumes.

    Zero production volumes occur when all inputs have been allocated to region-specific datasets."""
    filter_func = lambda x: x['type'] == 'market activity' and x['location'] == 'RoW'
    for ds in filter(filter_func, data):
        if production_volume(ds) == 0:
            logger.info({
                'type': 'table element',
                'data': (ds['name'], reference_products_as_string(ds))
            })
    return [ds for ds in data
            if (ds['location'] != 'RoW'
                or production_volume(ds) != 0
                or ds['type'] != 'market activity')]

drop_zero_pv_row_datasets.__table__ = {
    'title': 'Drop `RoW` datasets with zero production volumes',
    'columns': ["Name", "Product(s)"]
}
