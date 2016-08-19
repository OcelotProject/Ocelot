# -*- coding: utf-8 -*-
from ..utils import (
    allocatable_production,
    nonreference_product,
    remove_exchange_uncertainty,
)
from ..parameterization import recalculate
from .economic import economic_allocation
from .validation import valid_combined_production_activity
from copy import deepcopy
import itertools


def nonzero_reference_product_exchanges(dataset):
    """Return generator of all nonzero reference product exchanges"""
    return (exc for exc in dataset['exchanges']
            if exc['type'] == 'reference product'
            and exc['amount'])


def selected_product(exc):
    """Modify a production exchange to fix its numeric value.

    * Sets undertainty to no uncertainty
    * Deletes formula to prevent any changes in parameter evaluations.

    """
    if 'formula' in exc:
        del exc['formula']
    return remove_exchange_uncertainty(exc)


# def allocate_if_needed(ds):
#     if len(allocatable_production) > 1:
#         return economic_allocation(ds)
#     else:
#         return [ds]


@valid_combined_production_activity
def combined_production(dataset):
    """Perform subdivision of combined production activities.

    Combined production activities can vary the production of several reference products. As such, subdivision can be performed, and no allocation is needed. However, allocation may be needed for the resulting datasets, which may have byproducts.

    Subdivision assumes that the datasets are parameterized. Each reference product exchange should be a variable:

    .. code-block:: python

        {
            'type': 'reference production',
            'amount': 0.5,
            'variable': 'a_variable_name'
        }

    This variable can be referred to in other exchanges or parameters to determine the amounts of technosphere input or biosphere outputs.

    Subdivision is performed by iterating over the non-zero reference products, making a copy of the dataset, and setting the amount of all **other** reference product exchange variables to zero. We then recalculate the formulas and variables, and get the inputs needed for the production of only one reference product.

    Returns a list of new datasets."""
    new_datasets = []
    for exc in nonzero_reference_product_exchanges(dataset):
        new_ds, rp = deepcopy(dataset), deepcopy(exc)
        new_ds['exchanges'] = [selected_product(rp)] + \
            [nonreference_product(obj)
             for obj in nonzero_reference_product_exchanges(new_ds)
             if obj != exc] + \
            [deepcopy(obj) for obj in dataset['exchanges']
             if obj['type'] != 'reference product']
        new_datasets.append(recalculate(new_ds))
    return new_datasets
