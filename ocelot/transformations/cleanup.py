# -*- coding: utf-8 -*-
from ..data_helpers import (
    production_volume,
    reference_products_as_string,
)
import logging
import pprint


def ensure_all_datasets_have_production_volume(data):
    """Make sure all datasets have a single reference product exchange with a valid production volume amount"""
    for ds in data:
        assert production_volume(ds), "Dataset does not have valid production volume:\n{}".format(pprint.pformat(ds))
    return data


def drop_zero_pv_row_datasets(data):
    """Drop datasets which have the location ``RoW`` and zero production volumes.

    Zero production volumes occur when all inputs have been allocated to region-specific datasets."""
    for ds in (x for x in data if x['location'] == 'RoW'):
        if production_volume(ds) == 0:
            logging.info({
                'type': 'table element',
                'data': (ds['name'], reference_products_as_string(ds))
            })
    return [ds for ds in data
            if (ds['location'] != 'RoW' or production_volume(ds) != 0)]


drop_zero_pv_row_datasets.__table__ = {
    'title': 'Drop `RoW` datasets with zero production volumes',
    'columns': ["Name", "Product(s)"]
}