# -*- coding: utf-8 -*-
from ... import toolz
from ...data_helpers import reference_products_as_string, production_volume
from ..utils import activity_grouper, get_single_reference_product
from .validation import check_single_global_dataset
import logging


def relabel_global_to_row(data):
    """Change ``GLO`` locations to ``RoW`` if there are region-specific datasets in the activity group."""
    processed = []
    for key, datasets in toolz.groupby(activity_grouper, data).items():
        if len(datasets) > 1:
            check_single_global_dataset(datasets)

            for ds in datasets:
                if ds['location'] == 'GLO':
                    # Need to adjust production volume by subtracting the region-specific
                    # production volumes. We assume that each dataset has a single reference
                    # product with a production volume.
                    region_specific_pv = sum(
                        get_single_reference_product(obj)['production volume']['amount']
                        for obj in datasets
                        if obj != ds
                    )
                    rp = get_single_reference_product(ds)
                    rp['production volume']['amount'] = max(rp['production volume']['amount'] - region_specific_pv,0)

                    ds['location'] = 'RoW'
                    logging.info({
                        'type': 'table element',
                        # key is activity name and list of reference products
                        'data': (key[0], "; ".join(sorted(key[1])))
                    })
                processed.append(ds)
        else:
            processed.extend(datasets)
    return processed

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
            logging.info({
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
