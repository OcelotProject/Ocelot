# -*- coding: utf-8 -*-
import wrapt


def apply_allocation_factors(dataset, factors):
    # TODO
    return dataset, factors


@wrapt.decorator
def needs_allocation(wrapped, instance, args, kwargs):
    dataset, factors = wrapped(*args, **kwargs)
    return apply_allocation_factors(dataset, factors)


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
