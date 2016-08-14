# -*- coding: utf-8 -*-
from ..utils import get_single_reference_product
from .economic import economic_allocation


def recycling_allocation(dataset):
    """Allocate a recycling activity.

    A recycling dataset has a reference product of the material to be recycled, and a byproduct of the material that can enter a market. For example, TODO.

    This function will change the reference product to an input (meaning that it is now an allocatable input instead of an output), and then perform economic allocation."""
    rp = get_single_reference_product(dataset)
    rp['type'] = 'from technosphere'
    # TODO: Figure out about uncertainties
    rp['amount'] = -1 * rp['amount']
    return economic_allocation(dataset)
