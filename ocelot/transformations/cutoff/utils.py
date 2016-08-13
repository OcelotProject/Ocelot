# -*- coding: utf-8 -*-
import wrapt


def apply_allocation_factors(dataset, factors):
    # TODO
    return dataset, factors


@wrapt.decorator
def needs_allocation(wrapped, instance, args, kwargs):
    dataset, factors = wrapped(*args, **kwargs)
    return apply_allocation_factors(dataset, factors)
