# -*- coding: utf-8 -*-
from ... import toolz
from ..utils import get_single_reference_product
import logging


def flip_exchange(exc):
    """Flip amount and formula of an exchange"""
    exc['amount'] = -1 * exc['amount']
    if 'formula' in exc:
        exc['formula'] = '-1 * ({})'.format(exc['formula'])
    return exchange


def handle_constrained_markets(data):
    """Handle constrained markets and their activity links to transforming activities.

    We follow the `ecoinvent description <http://www.ecoinvent.org/support/faqs/methodology-of-ecoinvent-3/what-is-a-constrained-market-how-is-it-different-from-the-normal-market-how-does-it-behave-during-the-linking.html>`__ of constrained markets.

    A constrained exchange has the following attributes:

    * They only occur in market activities
    * They have a negative amount
    * They have the type ``byproduct``
    * They have an activity link
    * They have a property ``consequential`` with a value of 1

    We need to do the following:

    * Move the activity link constrained exchange from a byproduct to an input (and multiply amount by -1)
    * In the linked transforming activity, move the previous reference product to an input (and multiply amount by -1)
    * In the linked transforming activity, move the input with the same product name as the constrained exchange to a reference product (and multiply amount by -1)

    """
    id_mapping = {ds['id']: ds for ds in data}
    for ds in data:
        for exc in (e for e in ds['exchanges'] if e.get('conditional exchange')):
            target = id_mapping[exc['activity link']]

            # Handle exchange in this dataset
            exc['type'] = 'from technosphere'
            flip_exchange(exc)

            # Find and modify current target reference product
            target_rp = get_single_reference_product(target)
            target_rp['type'] = 'from technosphere'
            flip_exchange(target_rp)

            # Find and modify corresponding exchange in target
            target_excs = [e for e in target['exchanges'] if e['name'] == exc['name']]
            assert len(target_excs) == 1, "Can't find corresponding input"
            target_exc = target_excs[0]
            assert target_exc['type'] == 'from technosphere', "Wrong type for activity link target"
            target_exc['type'] = 'reference product'
            target_exc['byproduct classification'] = 'allocatable product'
            flip_exchange(target_exc)
    return data
