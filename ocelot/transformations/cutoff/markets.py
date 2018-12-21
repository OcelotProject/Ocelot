# -*- coding: utf-8 -*-
from . import RC_STRING
from ..utils import nonreference_product, get_single_reference_product
from ..uncertainty import scale_exchange
from ... import toolz
import logging

logger = logging.getLogger('ocelot')


def constrained_market_allocation(dataset):
    """Perform constrained market allocation on a dataset.

    A constrained market has one or more conditional exchanges which produce byproducts. These byproducts are constrained in the sense that increased demands of these byproducts will not increase their production, but rather will increase the production of other materials which can substitute for these byproducts. For more detail, see pp. 81-85 of the `data quality guidelines <http://www.ecoinvent.org/files/dataqualityguideline_ecoinvent_3_20130506.pdf>`__.

    In the cutoff system model, constrained byproducts are not used, and these exchanges can be set to zero.

    """
    conditional = (exc
                   for exc in dataset['exchanges']
                   if exc['type'] == 'byproduct'
                   and exc.get('conditional exchange'))
    for exc in conditional:
        logger.info({
            'type': 'table element',
            'data': (dataset['name'], exc['name']),
        })
        nonreference_product(exc)  # Modifies in-place
    return dataset

constrained_market_allocation.__table__ = {
    'title': 'Zero out conditional exchanges in cutoff model',
    'columns': ["Activity name", "Flow"]
}


def adjust_market_signs_for_allocatable_products(data):
    """If all exchanges (inputs and production) are negative, and the reference product is an ``allocatable product``, then flip signs to be positive.

    Only waste treatment activities should have negative reference products. Needed for consistency with published ecoinvent results.

    Some markets had their signs manually flipped, but their reference product is not ``waste``."""
    all_negative = lambda ds: all(exc['amount'] <= 0 for exc in ds['exchanges'])

    for ds in data:
        if (ds['type'] == 'market activity' and
            get_single_reference_product(ds)['byproduct classification'] != 'waste' and
            all_negative(ds)):
            logger.info({
                'type': 'table element',
                'data': [ds['name'], ds['location']],
            })
            for exc in ds['exchanges']:
                scale_exchange(exc, -1)
        # Sometimes just the reference product has a negative amount. Who knows why?
        # E.g. `market for 2,3-dimethylbutan`
        # We flip this because ecoinvent does. The world is a confusing place.
        elif (ds['type'] == 'market activity' and
            get_single_reference_product(ds)['byproduct classification'] != 'waste' and
            get_single_reference_product(ds)['amount'] < 0):
            logger.info({
                'type': 'table element',
                'data': [ds['name'], ds['location']],
            })
            rp = get_single_reference_product(ds)
            for exc in ds['exchanges']:
                if exc['name'] == rp['name']:
                    scale_exchange(exc, -1)

    return data

adjust_market_signs_for_allocatable_products.__table__ = {
    'title': 'Flip signs for negative non-waste markets',
    'columns': ["Activity name", "Location"]
}


def set_market_pv_when_consumer_recycled_content_cutoff(data):
    """Set artificial production volumes for markets which consumer products from ``Recycled Content, cut-off`` datasets. These datasets are artificial, and therefore have no production volume.

    See https://github.com/OcelotProject/Ocelot/issues/156."""
    market_filter = lambda x: x['type'] == "market activity"
    transforming_filter = lambda x: x['type'] == "transforming activity"
    rc_filter = lambda x: x['name'].endswith(RC_STRING)
    grouped = toolz.groupby("reference product", filter(transforming_filter, filter(rc_filter, data)))

    for ds in filter(transforming_filter, data):
        if ds['reference product'] in grouped:
            rp = get_single_reference_product(ds)
            rp['production volume'] = {"amount": 1}
            ds["production volume set by cutoff"] = True
            logger.info({
                'type': 'table element',
                'data': (
                    ds['name'],
                    ds['reference product'],
                    ds['location'],
                    grouped[ds['reference product']][0]['name']
                )
            })

    return data

set_market_pv_when_consumer_recycled_content_cutoff.__table__ = {
    'title': 'Add artificial production volumes for market consumers of recycled content activities',
    'columns': ["Name", "Product", "Location", "Provider"]
}
