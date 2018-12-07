# -*- coding: utf-8 -*-
from ..utils import nonreference_product, get_single_reference_product
from ..uncertainty import scale_exchange
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
            get_single_reference_product(ds)['byproduct classification'] == 'allocatable product' and
            all_negative(ds)):
            logger.info({
                'type': 'table element',
                'data': [ds['name'], ds['location']],
            })
            for exc in ds['exchanges']:
                scale_exchange(exc, -1)

    return data

adjust_market_signs_for_allocatable_products.__table__ = {
    'title': 'Flip signs for negative non-waste markets',
    'columns': ["Activity name", "Location"]
}
