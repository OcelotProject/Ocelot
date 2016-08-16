# -*- coding: utf-8 -*-
from ..utils import (
    allocatable_production,
    choose_reference_product_exchange,
    get_single_reference_product,
)
from .economic import economic_allocation
from .validation import valid_recycling_activity, valid_waste_treatment_activity
from copy import deepcopy


@valid_recycling_activity
def recycling_allocation(dataset):
    """Allocate a recycling activity.

    Returns a list of new activities.

    A recycling dataset has a reference product of the material to be recycled, and a byproduct of the material that can enter a market. For example, TODO.

    This function will change the reference product to an input (meaning that it is now an allocatable input instead of an output), and then perform economic allocation."""
    rp = get_single_reference_product(dataset)
    rp['type'] = 'from technosphere'
    # TODO: Figure out about uncertainties
    rp['amount'] = -1 * rp['amount']
    return economic_allocation(dataset)


@valid_waste_treatment_activity
def waste_treatment_allocation(dataset):
    """Perform cutoff system model allocation on a waste treatment activity.

    Returns a list of new activities.

    In the cutoff system model, the useful products of waste treatment come with no environmental burdens - they are cut off from the rest of the supply chain. So, this allocation function creates one dataset with all the environmental burdens which treats (consumes) the actual waste, and several new datasets which provide each byproduct for free.

    """
    def free_byproduct(dataset, exchange):
        """Create a new activity dataset with only one exchange"""
        new_one, byproduct = deepcopy(dataset), deepcopy(exchange)
        new_one['exchanges'] = [byproduct]
        # Label exchange as ref. product and normalize production amount
        return choose_reference_product_exchange(new_one, byproduct)

    rp = get_single_reference_product(dataset)
    return [
        choose_reference_product_exchange(dataset, rp)
    ] + [
        free_byproduct(dataset, exchange)
        for exchange in allocatable_production(dataset)
        if exchange is not rp
    ]
