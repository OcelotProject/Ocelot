# -*- coding: utf-8 -*-
from ..utils import nonreference_product
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
