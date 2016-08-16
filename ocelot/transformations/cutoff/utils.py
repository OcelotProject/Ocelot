# -*- coding: utf-8 -*-
from ..utils import choose_reference_product_exchange


def apply_allocation_factors(dataset, factors):
    """Apply allocation factors given in ``factors`` to ``dataset``.

    ``dataset`` is a normal activity dataset. ``factors`` has the data format: ``[(allocation factor, chosen reference product exchange)]``.

    Returns a list of ``len(factors)`` new datasets."""
    return [
        choose_reference_product_exchange(dataset, exc, scale)
        for scale, exc in factors
    ]


def flip_non_allocatable_byproducts(dataset):
    """Change non-allocatable byproducts from outputs to technosphere to inputs from technosphere.

    Non-allocatable byproducts have the classification ``recyclable`` or ``waste``.

    This has no effect on the technosphere matrix, and should not change the behaviour of any transformation functions, which should be testing for classification instead of exchange type. However, this is the current behaviour of the existing ecoinvent system model.

    Change something from an output to an input requires flipping the sign of any numeric fields."""
    for exc in dataset['exchanges']:
        if exc['type'] == 'byproduct' and exc['byproduct classification'] != 'allocatable':
            # TODO: Also need to change uncertainty?
            exc['type'] = 'from technosphere'
            del exc['byproduct classification']
            exc['amount'] = -1 * exc['amount']
            if 'formula' in exc:
                exc['formula'] = '-1 * ({})'.format(exc['formula'])
    return dataset
