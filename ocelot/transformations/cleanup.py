# -*- coding: utf-8 -*-
from ..data_helpers import (
    production_volume,
    reference_products_as_string,
)
from ..errors import InvalidMarketExchange, InvalidMarket
import logging
import pprint


def ensure_all_datasets_have_production_volume(data):
    """Make sure all datasets have a single reference product exchange with a valid production volume amount"""
    for ds in data:
        assert production_volume(ds), "Dataset does not have valid production volume:\n{}".format(pprint.pformat(ds))
    return data


def ensure_markets_only_have_one_reference_product(data):
    """"Markets are only allowed to have one reference product exchange.

    Raises ``InvalidMarket`` if multiple outputs were found."""
    for ds in (obj for obj in data if obj['type'] == 'market activity'):
        if sum(1 for exc in ds['exchanges'] if exc['type'] == 'reference product') != 1:
            message = "Market dataset has zero or multiple reference products:\{}"
            raise InvalidMarket(message.format(ds['filepath']))
    return data


def ensure_markets_dont_consume_their_ref_product(data):
    """Markets aren't allowed to consumer their own reference product.

    Raise ``InvalidMarketExchange`` if such an exchange is found.

    Direct (activity) links are excepted from this rule."""
    for ds in (obj for obj in data if obj['type'] == 'market activity'):
        rp = [exc for exc in ds['exchanges'] if exc['type'] == 'reference product'][0]
        if any(exc for exc in ds['exchanges']
               if exc['name'] == rp['name']
               and exc != rp
               and not exc.get("activity link")):
            message = "Market dataset has exchanges which consume the ref. product:\n{}"
            raise InvalidMarketExchange(message.format(ds['filepath']))
    return data


def count_same_as_rp(ds):
    rp = get_single_reference_product(ds)
    return sum(1 for exc in ds['exchanges']
               if exc['name'] == rp['name']
               and exc != rp
               and not exc.get("activity link"))


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
