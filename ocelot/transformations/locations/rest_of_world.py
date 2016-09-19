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
            # start non-GLO production volume at zero and set ds_GLO (the potential global dataset) to None. 
            # This is so if there's no GLO it doesnt add a second version of the one from the previous loop
            non_GLO_pv = 0
            ds_GLO = None
            
            check_single_global_dataset(datasets)
            
            for ds in datasets:
                # Identify and store the GLO dataset, change it to RoW, but don't add to processed yet
                if ds['location'] == 'GLO':
                    ds_GLO = ds
                    ds['location'] = 'RoW'
                    logging.info({
                        'type': 'table element',
                        'data': (key[0], "; ".join(sorted(key[1])))
                    })
                # get the production volume from the non-GLO transformations and add it to the running total, then add it to processed
                else:
                    rp = get_single_reference_product(ds)
                    non_GLO_pv += rp['production volume']['amount']

                    processed.append(ds)

            # subtract the non-GLO production volume from the GLO/RoW process and then append it too
            if ds_GLO is not None:
                rp_GLO = get_single_reference_product(ds_GLO)
                rp_GLO['production volume']['amount'] -= non_GLO_pv
                if rp_GLO['production volume']['amount'] < 0:
                    rp_GLO['production volume']['amount'] = 0
                processed.append(ds_GLO)

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
