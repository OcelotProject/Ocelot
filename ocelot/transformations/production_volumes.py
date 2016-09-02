# -*- coding: utf-8 -*-
from .utils import get_biggest_pv_to_exchange_ratio
import logging


def add_pv_to_allocatable_byproducts(data):
    """Add production volumes to allocatable byproducts based on reference product production volume.

    Allocatable byproducts will be separated into new datasets, and need production volumes so they be correctly allocated to markets.

    Skips allocatable byproducts which already have a production volume."""
    bp_filter = lambda x: (x['type'] == 'byproduct'
                           and x['byproduct classification'] == 'allocatable product')
    for ds in data:
        if any(filter(bp_filter, ds['exchanges'])):
            scale = get_biggest_pv_to_exchange_ratio(ds)
            for exc in filter(bp_filter, ds['exchanges']):
                if not exc['production volume']['amount']:
                    # Need ``abs`` because can have positive byproduct amount
                    # from waste treatment with negative production amount
                    exc['production volume']['amount'] = \
                        abs(exc['amount'] * scale)
                    logging.info({
                        'type': 'table element',
                        'data': (ds['name'], exc['name'], abs(exc['amount'] * scale))
                    })
    return data

add_pv_to_allocatable_byproducts.__table__ = {
    'title': 'Add production volume amounts to allocatable byproducts',
    'columns': ["Name", "Flow", "Production volume"]
}
